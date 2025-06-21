from sqlalchemy.orm  import relationship
from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, Boolean, Enum, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    parent = relationship("Category", remote_side=[id], backref="children")

class Facility(Base):
    __tablename__ = "facilities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)

    has_parking = Column(Boolean)
    elevator = Column(Boolean)
    kitchen = Column(Boolean)
    power_car = Column(Boolean)
    protection = Column(Boolean)
    electric_available = Column(Boolean)
    electric_capacity = Column(String(100))
    special_equipment = Column(Boolean)
    sound_recording_ok = Column(Boolean)
    fire_usage = Column(Boolean)
    extra_notes = Column(Text)

    location = relationship("Location", backref="facility")

class LocationCategory(Base):
    __tablename__ = "locationcategories"

    location_id = Column(Integer, ForeignKey("locations.id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), primary_key=True)

class LocationImage(Base):
    __tablename__ = "locationimages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    image_type = Column(String(100))
    image_url = Column(Text)
    caption = Column(String(255))

    location = relationship("Location", backref="images")

payment_enum = Enum('現金', '請求書', 'カード', '不明', name="payment_method")

class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    slug = Column(String(255, collation="utf8mb4_0900_ai_ci"))
    tel = Column(String(50))
    mail = Column(String(255))
    contact_name = Column(String(255))
    available_time_from = Column(String(100, collation="utf8mb4_0900_ai_ci"))
    available_time_to = Column(String(100, collation="utf8mb4_0900_ai_ci"))
    price_movie_day = Column(Integer)
    price_movie_h = Column(Integer)
    price_movie_notes = Column(Text(collation="utf8mb4_0900_ai_ci"))
    payment_method = Column(payment_enum)
    payment_due = Column(String(50))
    capacity = Column(Integer)
    area_sqm = Column(Float)
    ceiling_height = Column(Float)
    remarks = Column(Text)
    address = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    access_info = Column(Text(collation="utf8mb4_0900_ai_ci"))
    map_url = Column(String(255))
    hp_url = Column(String(255))
    is_published = Column(Boolean)
    deleted_at = Column(DateTime)
    created_by = Column(String(255))
    created_at = Column(DateTime)
    updated_by = Column(String(255))
    updated_at = Column(DateTime)


class LocationTag(Base):
    __tablename__ = "locationtags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=True)

class Option(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True, autoincrement=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    camera_info = Column(Text)
    pool_info = Column(Text)
    other = Column(Text)

    location = relationship("Location", backref="option")


class PastWork(Base):
    __tablename__ = "pastworks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    product_id = Column(String(36), nullable=False)

    location = relationship("Location", backref="pastworks")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tag_name = Column(String(255), nullable=False, unique=True)