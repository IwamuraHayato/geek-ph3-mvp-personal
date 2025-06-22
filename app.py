from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json
from db_control.connect_MySQL import SessionLocal
from db_control import crud, mymodels_MySQL
from db_control.crud import get_location_detail_by_id, get_all_categories
from dotenv import load_dotenv
import os
from sqlalchemy.orm import Session
from datetime import datetime,timedelta,date
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import ContentSettings
import uuid
from typing import List, Optional

load_dotenv()

app = FastAPI()

@app.get("/")
def index():
    return {"message": "FastAPI top page!!"}

#######################
# カテゴリ取得
#######################

@app.get("/api/categories")
def get_categories():
    """
    category一覧を返すエンドポイント
    """
    result = get_all_categories()
    if result is None:
        raise HTTPException(status_code=404, detail="ロケーションが見つかりませんでした")
    return result


#######################
# ロケーション詳細取得
#######################

@app.get("/locations/{location_id}")
def get_location_detail(location_id: int):
    """
    指定された location_id のロケーション詳細を返すエンドポイント
    """
    result = get_location_detail_by_id(location_id)
    if result is None:
        raise HTTPException(status_code=404, detail="ロケーションが見つかりませんでした")
    return result


#######################
# 以下AI search
#######################

from fastapi import Query
from typing import Optional, List
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

# Azure Cognitive Search接続情報
SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
SEARCH_ADMIN_KEY = os.getenv("SEARCH_ADMIN_KEY")
INDEX_NAME = os.getenv("INDEX_NAME")


@app.get("/api/locations/ai-search")
def ai_search(
    keyword: str = "*",
    categories: Optional[List[str]] = Query(None),
    area_keyword: Optional[str] = None,
    price_day_min: Optional[int] = None,
    price_day_max: Optional[int] = None,
    price_hour_min: Optional[int] = None,
    price_hour_max: Optional[int] = None,
    facilities: Optional[List[str]] = Query(None),
    payment_method: Optional[List[str]] = Query(None),
    payment_due: Optional[str] = None,
    people_min: Optional[int] = None,
    people_max: Optional[int] = None,
    time_min: Optional[int] = None,
    time_max: Optional[int] = None,
    area_min: Optional[float] = None,
    area_max: Optional[float] = None,
    ceiling_min: Optional[float] = None,
    ceiling_max: Optional[float] = None,
):
    try:
        # クライアント生成
        credential = AzureKeyCredential(SEARCH_ADMIN_KEY)
        client = SearchClient(endpoint=SEARCH_ENDPOINT, index_name=INDEX_NAME, credential=credential)

        # クエリフィルター組み立て
        filters = []

        if categories:
            category_filters = [f"categories/any(c: c eq '{cat}')" for cat in categories]
            filters.append(f"({' or '.join(category_filters)})")

        if price_day_min is not None:
            filters.append(f"price_movie_day ge {price_day_min}")
        if price_day_max is not None:
            filters.append(f"price_movie_day le {price_day_max}")

        if price_hour_min is not None:
            filters.append(f"price_movie_h ge {price_hour_min}")
        if price_hour_max is not None:
            filters.append(f"price_movie_h le {price_hour_max}")

        if facilities:
            for facility in facilities:
                filters.append(f"facilities/{facility} eq true")

        if payment_method:
            payment_filters = [f"payment_method eq '{method}'" for method in payment_method]
            filters.append(f"({' or '.join(payment_filters)})")

        if payment_due:
            filters.append(f"payment_due eq '{payment_due}'")

        if people_min is not None:
            filters.append(f"max_people ge {people_min}")
        if people_max is not None:
            filters.append(f"max_people le {people_max}")

        if time_min is not None:
            filters.append(f"available_hours ge {time_min}")
        if time_max is not None:
            filters.append(f"available_hours le {time_max}")

        if area_min is not None:
            filters.append(f"area_sqm ge {area_min}")
        if area_max is not None:
            filters.append(f"area_sqm le {area_max}")

        if ceiling_min is not None:
            filters.append(f"ceiling_height ge {ceiling_min}")
        if ceiling_max is not None:
            filters.append(f"ceiling_height le {ceiling_max}")

        filter_query = " and ".join(filters) if filters else None
        combined_keyword = keyword if not area_keyword else f"{keyword} {area_keyword}"

        # 検索実行
        search_results = client.search(
            search_text=combined_keyword,
            filter=filter_query,
            facets=["categories"],
            query_type="semantic",
            semantic_configuration_name="default"
        )

        # 結果整形
        documents = [dict(r) for r in search_results]
        facets = search_results.get_facets()

        return {"results": documents, "facets": facets}
    
    except Exception as e:
        print(f"AIサーチエラー: {e}")
        raise HTTPException(status_code=500, detail="AIサーチの実行に失敗しました")
