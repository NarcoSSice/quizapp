"""empty message

Revision ID: dfa2db2c70e3
Revises: 5c25b36d6e9e
Create Date: 2025-08-18 10:29:22.334489

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "dfa2db2c70e3"
down_revision: Union[str, Sequence[str], None] = "29536ba46e3d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "quiz_results",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
    )
    op.drop_constraint("quiz_results_pkey", "quiz_results", type_="primary")
    op.create_primary_key("quiz_results_pkey", "quiz_results", ["id"])

    op.create_index(
        op.f("ix_quiz_results_company_id"), "quiz_results", ["company_id"], unique=False
    )
    op.create_index(
        op.f("ix_quiz_results_quiz_id"), "quiz_results", ["quiz_id"], unique=False
    )
    op.create_index(
        op.f("ix_quiz_results_user_id"), "quiz_results", ["user_id"], unique=False
    )

    op.create_table(
        "user_quiz_answers",
        sa.Column("quiz_result_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("user_answer", sa.ARRAY(sa.Integer()), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["quiz_result_id"], ["quiz_results.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_user_quiz_answers_question_id"),
        "user_quiz_answers",
        ["question_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_quiz_answers_quiz_result_id"),
        "user_quiz_answers",
        ["quiz_result_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_user_quiz_answers_quiz_result_id"), table_name="user_quiz_answers"
    )
    op.drop_index(
        op.f("ix_user_quiz_answers_question_id"), table_name="user_quiz_answers"
    )
    op.drop_table("user_quiz_answers")

    op.drop_index(op.f("ix_quiz_results_user_id"), table_name="quiz_results")
    op.drop_index(op.f("ix_quiz_results_quiz_id"), table_name="quiz_results")
    op.drop_index(op.f("ix_quiz_results_company_id"), table_name="quiz_results")

    op.drop_constraint("quiz_results_pkey", "quiz_results", type_="primary")
    op.drop_column("quiz_results", "id")
    op.create_primary_key(
        "quiz_results_pkey", "quiz_results", ["user_id", "company_id", "quiz_id"]
    )
