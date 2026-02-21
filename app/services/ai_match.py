"""AI matching service using OpenAI."""
from typing import Optional
import json
from openai import AsyncOpenAI

from app.config import config


class AIMatchService:
    """AI-powered resume matching service."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize AI match service.

        Args:
            api_key: OpenAI API key
        """
        self.api_key = api_key or config.openai_api_key
        self.model = config.openai_model
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None

    async def match_resume_to_job(
        self,
        job_description: str,
        job_requirements: str,
        resume_content: str,
    ) -> dict:
        """Match resume to job description.

        Args:
            job_description: Job description
            job_requirements: Job requirements
            resume_content: Resume content

        Returns:
            Match result with score (0-100) and reasons
        """
        if not self.client:
            # Return mock data if no API key
            return self._mock_match(job_description, resume_content)

        try:
            prompt = self._build_match_prompt(job_description, job_requirements, resume_content)
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional HR assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=500,
            )

            result_text = response.choices[0].message.content
            return self._parse_match_result(result_text)

        except Exception as e:
            # Fall back to mock on error
            return self._mock_match(job_description, resume_content)

    def _build_match_prompt(
        self,
        job_description: str,
        job_requirements: str,
        resume_content: str,
    ) -> str:
        """Build prompt for matching."""
        return f"""请分析以下简历与岗位的匹配度。

岗位描述:
{job_description}

岗位要求:
{job_requirements}

简历内容:
{resume_content}

请返回JSON格式的匹配结果:
{{
    "score": 0-100的匹配分数,
    "reasons": ["匹配理由1", "匹配理由2", "不匹配理由1"]
}}

只返回JSON，不要其他内容。"""

    def _parse_match_result(self, result_text: str) -> dict:
        """Parse match result from AI response."""
        try:
            # Extract JSON from response
            if "{" in result_text:
                json_str = result_text[result_text.index("{"):result_text.rindex("}")+1]
                result = json.loads(json_str)
                return {
                    "score": result.get("score", 0),
                    "reasons": result.get("reasons", []),
                }
        except Exception:
            pass

        return {"score": 0, "reasons": ["解析失败"]}

    def _mock_match(self, job_description: str, resume_content: str) -> dict:
        """Generate mock match result for testing."""
        # Simple keyword-based matching for mock
        job_keywords = set(job_description.lower().split())
        resume_keywords = set(resume_content.lower().split())
        common_keywords = job_keywords & resume_keywords

        if not job_keywords:
            score = 0
        else:
            score = min(100, int(len(common_keywords) / len(job_keywords) * 100))

        # Boost score for common scenarios
        if not resume_content or resume_content == "无":
            score = 0

        reasons = []
        if score > 70:
            reasons.append("技能匹配度高")
        if score > 50:
            reasons.append("有一定相关经验")
        if score < 30:
            reasons.append("技能匹配度较低")

        return {"score": score, "reasons": reasons}


# Singleton instance
_ai_match_service = None


def get_ai_match_service() -> AIMatchService:
    """Get singleton AI match service."""
    global _ai_match_service
    if _ai_match_service is None:
        _ai_match_service = AIMatchService()
    return _ai_match_service
