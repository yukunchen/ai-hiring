"""Email generation service using AI."""
from typing import Optional
import re
from openai import AsyncOpenAI

from app.config import config


class EmailGenerationService:
    """AI-powered email generation service."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize email generation service.

        Args:
            api_key: OpenAI API key
        """
        self.api_key = api_key or config.openai_api_key
        self.model = config.openai_model
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None

    async def generate_inquiry_email(
        self,
        candidate_name: str,
        job_title: str,
        company_name: str = "贵公司",
    ) -> dict:
        """Generate candidate inquiry email.

        Args:
            candidate_name: Candidate's name
            job_title: Job position title
            company_name: Company name

        Returns:
            Generated email with subject and body
        """
        if not self.client:
            return self._generate_mock_email(candidate_name, job_title, company_name)

        try:
            prompt = self._build_email_prompt(candidate_name, job_title, company_name)
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一名前招聘HR，擅长撰写专业、友好的招聘邮件。"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=1000,
            )

            content = response.choices[0].message.content
            return self._parse_email_content(content, candidate_name, job_title)

        except Exception:
            return self._generate_mock_email(candidate_name, job_title, company_name)

    def _build_email_prompt(
        self,
        candidate_name: str,
        job_title: str,
        company_name: str,
    ) -> str:
        """Build prompt for email generation."""
        return f"""请为以下候选人生成一封求职意向询问邮件:

候选人姓名: {candidate_name}
应聘职位: {job_title}
公司名称: {company_name}

要求:
1. 邮件主题简洁明了
2. 邮件内容专业、友好、真诚
3. 简要说明来源和职位
4. 询问对方是否有兴趣
5. 留下联系方式
6. 中文邮件

请按以下格式返回:
---
主题: [邮件主题]

正文:
[邮件正文]
---
"""

    def _parse_email_content(
        self,
        content: str,
        candidate_name: str,
        job_title: str,
    ) -> dict:
        """Parse email content from AI response."""
        lines = content.strip().split("\n")
        subject = ""
        body_lines = []
        in_body = False

        for line in lines:
            if line.startswith("主题:") or line.startswith("Subject:"):
                subject = line.split(":", 1)[1].strip()
                in_body = True
            elif in_body:
                body_lines.append(line)

        if not subject:
            # Try to extract subject
            subject = f"关于 {job_title} 职位咨询"

        body = "\n".join(body_lines).strip()

        return {
            "subject": subject,
            "body": body,
            "to": candidate_name,
        }

    def _generate_mock_email(
        self,
        candidate_name: str,
        job_title: str,
        company_name: str,
    ) -> dict:
        """Generate mock email for testing."""
        subject = f"【{company_name}】关于 {job_title} 职位机会咨询"

        body = f"""尊敬的{candidate_name}您好:

我在{candidate_name}的简历中了解到您目前从事{job_title}相关工作，非常欣赏您的专业背景。

我们公司正在招聘{job_title}职位，认为您的经验与我们的需求非常匹配。

想借此机会与您进一步沟通，了解您目前的工作状况以及对这份职位的兴趣。

如您方便，请回复此邮件或拨打以下电话与我联系: [联系电话]

期待您的回复!

祝好
HR 团队
"""

        return {
            "subject": subject,
            "body": body,
            "to": candidate_name,
        }

    def validate_email(self, email: str) -> bool:
        """Validate email format.

        Args:
            email: Email address

        Returns:
            True if valid, False otherwise
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))


# Singleton instance
_email_service = None


def get_email_service() -> EmailGenerationService:
    """Get singleton email service."""
    global _email_service
    if _email_service is None:
        _email_service = EmailGenerationService()
    return _email_service
