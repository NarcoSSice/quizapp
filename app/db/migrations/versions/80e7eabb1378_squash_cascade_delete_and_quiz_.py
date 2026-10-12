"""squash cascade delete and quiz migrations

Revision ID: 80e7eabb1378
Revises: 3b475b1d07fa
Create Date: 2025-08-07 11:25:50.718340

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "80e7eabb1378"
down_revision: Union[str, Sequence[str], None] = "77b2114afc5f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        op.f("user_company_association_user_id_fkey"),
        "user_company_association",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("user_company_association_company_id_fkey"),
        "user_company_association",
        type_="foreignkey",
    )
    op.create_foreign_key(
        None,
        "user_company_association",
        "companies",
        ["company_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        None,
        "user_company_association",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Cascading deletion for company_actions
    op.drop_constraint(
        op.f("company_actions_user_id_fkey"), "company_actions", type_="foreignkey"
    )
    op.create_foreign_key(
        None, "company_actions", "users", ["user_id"], ["id"], ondelete="CASCADE"
    )

    # Creating quiz tables
    op.create_table(
        "quizzes",
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("total_attempts", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "questions",
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("quiz_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["quiz_id"], ["quizzes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "answers",
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("answers")
    op.drop_table("questions")
    op.drop_table("quizzes")

    op.drop_constraint(None, "company_actions", type_="foreignkey")
    op.create_foreign_key(
        op.f("company_actions_user_id_fkey"),
        "company_actions",
        "users",
        ["user_id"],
        ["id"],
    )

    op.drop_constraint(None, "user_company_association", type_="foreignkey")
    op.drop_constraint(None, "user_company_association", type_="foreignkey")
    op.create_foreign_key(
        op.f("user_company_association_company_id_fkey"),
        "user_company_association",
        "companies",
        ["company_id"],
        ["id"],
    )
    op.create_foreign_key(
        op.f("user_company_association_user_id_fkey"),
        "user_company_association",
        "users",
        ["user_id"],
        ["id"],
    )
