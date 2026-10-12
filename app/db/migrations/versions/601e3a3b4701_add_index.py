"""add index

Revision ID: 601e3a3b4701
Revises: 80e7eabb1378
Create Date: 2025-08-10 12:17:20.475897

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "601e3a3b4701"
down_revision: Union[str, Sequence[str], None] = "80e7eabb1378"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        op.f("ix_answers_question_id"), "answers", ["question_id"], unique=False
    )
    op.create_index(
        op.f("ix_companies_owner_id"), "companies", ["owner_id"], unique=False
    )
    op.create_index(
        op.f("ix_company_actions_company_id"),
        "company_actions",
        ["company_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_company_actions_user_id"), "company_actions", ["user_id"], unique=False
    )
    op.create_index(
        op.f("ix_questions_quiz_id"), "questions", ["quiz_id"], unique=False
    )
    op.create_index(
        op.f("ix_quizzes_company_id"), "quizzes", ["company_id"], unique=False
    )
    op.create_index(
        op.f("ix_user_company_association_company_id"),
        "user_company_association",
        ["company_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_company_association_user_id"),
        "user_company_association",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_user_company_association_user_id"),
        table_name="user_company_association",
    )
    op.drop_index(
        op.f("ix_user_company_association_company_id"),
        table_name="user_company_association",
    )
    op.drop_index(op.f("ix_quizzes_company_id"), table_name="quizzes")
    op.drop_index(op.f("ix_questions_quiz_id"), table_name="questions")
    op.drop_index(op.f("ix_company_actions_user_id"), table_name="company_actions")
    op.drop_index(op.f("ix_company_actions_company_id"), table_name="company_actions")
    op.drop_index(op.f("ix_companies_owner_id"), table_name="companies")
    op.drop_index(op.f("ix_answers_question_id"), table_name="answers")
