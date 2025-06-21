from sqlalchemy import insert, select, func
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from datetime import date

from db_control import mymodels_MySQL as models
from db_control.connect_MySQL import engine
from .mymodels_MySQL import (Category, Facility, Location, LocationCategory, LocationImage, LocationTag,Option, PastWork,Tag)

Session = sessionmaker(bind=engine)

@contextmanager
def session_scope():
    """
    セッションを安全に管理するためのスコープを提供。
    トランザクションの開始、ロールバック、クローズを自動で処理。
    """
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"セッションのエラー: {e}")
        raise
    finally:
        session.close()


def get_all_categories():
    try:
        with session_scope() as session:
            categories = session.query(Category).all()
            result = [{"id": c.id, "name": c.name, "parent_id": c.parent_id} for c in categories]
        return result
    
    except Exception as e:
        print(f"カテゴリ取得エラー: {e}")
        raise


def get_location_detail_by_id(location_id: int):
    try:
        with session_scope() as session:
            location = session.query(models.Location).filter(models.Location.id == location_id).first()
            if not location:
                return None

            categories = [
                c.name for c in session.query(models.Category)
                .join(models.LocationCategory, models.LocationCategory.category_id == models.Category.id)
                .filter(models.LocationCategory.location_id == location_id).all()
            ]

            tags = [
                t.tag_name for t in session.query(models.Tag)
                .join(models.LocationTag, models.LocationTag.tag_id == models.Tag.id)
                .filter(models.LocationTag.location_id == location_id).all()
            ]

            images = [
                {"image_type": img.image_type, "url": img.image_url, "caption": img.caption}
                for img in location.images
            ]

            facility = None
            if location.facility:
                facility = {
                    "has_parking": location.facility.has_parking,
                    "elevator": location.facility.elevator,
                    "kitchen": location.facility.kitchen,
                    "power_car": location.facility.power_car,
                    "protection": location.facility.protection,
                    "electric_available": location.facility.electric_available,
                    "electric_capacity": location.facility.electric_capacity,
                    "special_equipment": location.facility.special_equipment,
                    "sound_recording_ok": location.facility.sound_recording_ok,
                    "fire_usage": location.facility.fire_usage,
                    "extra_notes": location.facility.extra_notes,
                }

            option = None
            if location.option:
                option = {
                    "camera_info": location.option.camera_info,
                    "pool_info": location.option.pool_info,
                    "other": location.option.other,
                }

            pastworks = [
                pw.product_id for pw in location.pastworks
            ]

            return {
                "id": location.id,
                "name": location.name,
                "slug": location.slug,
                "tel": location.tel,
                "mail": location.mail,
                "contact_name": location.contact_name,
                "available_time_from": location.available_time_from,
                "available_time_to": location.available_time_to,
                "price_movie_day": location.price_movie_day,
                "price_movie_h": location.price_movie_h,
                "price_movie_notes": location.price_movie_notes,
                "payment_method": location.payment_method,
                "payment_due": location.payment_due,
                "capacity": location.capacity,
                "area_sqm": location.area_sqm,
                "ceiling_height": location.ceiling_height,
                "remarks": location.remarks,
                "address": location.address,
                "latitude": location.latitude,
                "longitude": location.longitude,
                "access_info": location.access_info,
                "map_url": location.map_url,
                "hp_url": location.hp_url,
                "is_published": location.is_published,
                "deleted_at": location.deleted_at.isoformat() if location.deleted_at else None,
                "created_by": location.created_by,
                "created_at": location.created_at.isoformat() if location.created_at else None,
                "updated_by": location.updated_by,
                "updated_at": location.updated_at.isoformat() if location.updated_at else None,
                "categories": categories,
                "tags": tags,
                "images": images,
                "facility": facility,
                "option": option,
                "pastworks": pastworks,
            }
    except Exception as e:
        print(f"ロケーション取得エラー: {e}")
        raise