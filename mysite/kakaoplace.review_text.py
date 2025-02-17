import os
import django
import time
import google.api_core.exceptions
import google.generativeai as genai

# ✅ Django 환경 설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from kakao_api.models import kakaoplace  # ✅ `Review` 모델이 아닌 `kakaoplace` 사용

# ✅ API 키 설정 (config.json에서 로드)
import json
with open("config.json", "r") as config_file:
    config = json.load(config_file)
    GEMINI_API_KEY = config["GEMINI_API_KEY"]

# ✅ Gemini API 설정
genai.configure(api_key=GEMINI_API_KEY)

def generate_review_summary(review_text):
    """Gemini를 이용해 `review_text` 필드의 리뷰를 요약"""
    if not review_text:
        return "❌ 요약할 리뷰 없음"

    model = genai.GenerativeModel("gemini-pro")

    prompt_text = f"""
    다음은 한 장소에 대한 리뷰입니다.
    - 리뷰: {review_text[:2000]}  # ✅ 너무 길면 2000자까지만 사용
    이 리뷰의 핵심 내용을 한 줄로 요약해주세요.
    """

    retry_attempts = 3  # ✅ 최대 3번 재시도
    for attempt in range(retry_attempts):
        try:
            response = model.generate_content(prompt_text)
            time.sleep(2)  # ✅ API 과부하 방지

            if not response.candidates:
                print(f"⚠️ Gemini API 응답 없음: {response}")
                return "요약 실패 (응답 없음)"

            candidate = response.candidates[0]
            return candidate.content.parts[0].text.strip() if candidate.content.parts else "❌ 요약 실패"

        except google.api_core.exceptions.ResourceExhausted:
            print(f"⚠️ Gemini API 할당량 초과! {attempt + 1}/{retry_attempts}회 재시도 중...")
            time.sleep(5)
        except Exception as e:
            print(f"⚠️ Gemini API 호출 오류: {e}")
            return "요약 실패"

    return "요약 실패 (할당량 초과)"  # 3번 재시도 후에도 실패하면 오류 메시지 반환

def update_review_summaries():
    """DB의 `kakaoplace.review_text` 데이터를 요약하여 저장"""
    places = kakaoplace.objects.all()

    for place in places:
        if place.review_text:  # ✅ `review_text`가 존재하는 경우에만 처리
            summary = generate_review_summary(place.review_text)
            
            # ✅ 요약된 내용을 저장할 새로운 필드 추가
            place.review_summary = summary  # ⚠️ `review_summary` 필드가 존재하는지 확인 필요!
            place.save()
            print(f"✅ '{place.name}' 리뷰 요약 완료: {summary}")

if __name__ == "__main__":
    update_review_summaries()
