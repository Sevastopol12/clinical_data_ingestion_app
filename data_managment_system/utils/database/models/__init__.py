from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Text


class Base(DeclarativeBase):
    pass


class Report(Base):
    __tablename__ = "report"
    __table_args__ = {"schema": "Landing"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    ma_bhyt: Mapped[str] = mapped_column(Text, unique=True)
    cccd: Mapped[str] = mapped_column(Text, unique=True)
    ma_bn: Mapped[str] = mapped_column(Text)

    ho_ten: Mapped[str] = mapped_column(Text, nullable=True)
    gioi_tinh: Mapped[str] = mapped_column(Text, nullable=True)
    nam_sinh: Mapped[str] = mapped_column(Text, nullable=True)
    dia_chi: Mapped[str] = mapped_column(Text, nullable=True)
    ngay_kham: Mapped[str] = mapped_column(Text, nullable=True)

    icd_tha: Mapped[str] = mapped_column(Text, nullable=True)
    icd_dtd: Mapped[str] = mapped_column(Text, nullable=True)
    chi_so_huyet_ap: Mapped[str] = mapped_column(Text, nullable=True)
    chi_so_duong_huyet: Mapped[str] = mapped_column(Text, nullable=True)
    chi_so_khac: Mapped[str] = mapped_column(Text, nullable=True)

    ghi_chu: Mapped[str] = mapped_column(Text, nullable=True)
    dieu_tri: Mapped[str] = mapped_column(Text, nullable=True)


__all__ = ["Report"]
