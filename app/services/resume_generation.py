"""Resume generation service using AI."""
from typing import Optional
from openai import AsyncOpenAI

from app.config import config


class ResumeGenerationService:
    """AI-powered resume generation service."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize resume generation service.

        Args:
            api_key: OpenAI API key
        """
        self.api_key = api_key or config.openai_api_key
        self.model = config.openai_model
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None

    async def generate_resume_from_info(
        self,
        name: str,
        title: Optional[str] = None,
        company: Optional[str] = None,
        experience: Optional[str] = None,
        source: Optional[str] = None,
    ) -> str:
        """Generate resume content from candidate basic info.

        Args:
            name: Candidate name
            title: Current job title
            company: Current company
            experience: Years of experience
            source: Source platform

        Returns:
            Generated resume content
        """
        if not self.client:
            return self._generate_mock_resume(name, title, company, experience, source)

        prompt = self._build_resume_prompt(name, title, company, experience, source)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一名前招聘HR，擅长根据候选人的基本信息生成专业、真实的简历内容。",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=1500,
            )

            return response.choices[0].message.content

        except Exception as e:
            # Fall back to mock on error
            return self._generate_mock_resume(name, title, company, experience, source)

    def _build_resume_prompt(
        self,
        name: str,
        title: Optional[str],
        company: Optional[str],
        experience: Optional[str],
        source: Optional[str],
    ) -> str:
        """Build prompt for resume generation."""
        info_parts = [f"- 姓名：{name}"]

        if title:
            info_parts.append(f"- 当前职位：{title}")
        if company:
            info_parts.append(f"- 当前公司：{company}")
        if experience:
            info_parts.append(f"- 工作年限：{experience}")
        if source:
            source_names = {"liepin": "猎聘", "zhipin": "BOSS直聘", "linkedin": "LinkedIn"}
            source_name = source_names.get(source, source)
            info_parts.append(f"- 来源平台：{source_name}")

        info_str = "\n".join(info_parts)

        return f"""根据以下候选人基本信息，生成一份模拟的简历内容，包括：
1. 个人简介（50-100字）
2. 主要工作经历（1-2段）
3. 项目经历（2-3个具体项目）
4. 技能专长（技术技能和软技能）

候选人信息：
{info_str}

请生成一份专业、结构化的简历内容，使用中文。"""

    def _generate_mock_resume(
        self,
        name: str,
        title: Optional[str],
        company: Optional[str],
        experience: Optional[str],
        source: Optional[str],
    ) -> str:
        """Generate mock resume for testing."""
        title_str = title or "工程师"
        company_str = company or "某公司"
        exp_str = experience or "1-3年"

        return f"""【个人简介】
{name}，当前担任{title_str}，拥有{exp_str}的工作经验。

【主要工作经历】
- {company_str}，{title_str}
  负责相关技术工作，参与多个项目的开发和维护。

【项目经历】
- 参与公司核心项目开发
- 负责系统架构设计与优化
- 主导技术难题攻关

【技能专长】
- 熟练掌握专业技能
- 具备良好的团队协作能力
- 善于分析和解决问题"""


# Singleton instance
_resume_service = None


def get_resume_generation_service() -> ResumeGenerationService:
    """Get singleton resume generation service."""
    global _resume_service
    if _resume_service is None:
        _resume_service = ResumeGenerationService()
    return _resume_service
