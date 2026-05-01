from dataclasses import dataclass
from typing import List, Dict
import requests
import xml.etree.ElementTree as ET

@dataclass
class Article:
    law_name: str
    article_number: str
    text: str

# ✅ 正しいLawID（または法令番号）を指定する必要があります
# e-Gov API v1では、法令番号（例: 明治二十九年法律第八十九号）でも取得可能です
LAW_ID_DICT = {
   # "民法": "明治二十九年法律第八十九号",
    "刑法": "明治四十年法律第四十五号",
    "労働施策総合推進法": "昭和四十一年法律第百三十二号", # 追加
}

def get_articles(law_name: str) -> Dict[str, List[Article]]:
    law_id = LAW_ID_DICT.get(law_name)
    if not law_id:
        print(f"Law name '{law_name}' not found in dictionary.")
        return {law_name: []}

    # e-Gov API v1 のエンドポイント
    url = f"https://laws.e-gov.go.jp/api/1/lawdata/{law_id}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print("REQUEST ERROR:", e)
        return {law_name: []}

    articles = _parse_xml(response.text, law_name)
    return {law_name: articles}

def _parse_xml(xml_text: str, law_name: str) -> List[Article]:
    try:
        root = ET.fromstring(xml_text.encode('utf-8'))
    except ET.ParseError as e:
        print("XML PARSE ERROR:", e)
        return []

    results = []

    # ✅ e-Gov APIのXML構造に対応
    # LawFullText ではなく、トップレベルから Article を探す
    # 多くの場合、名前空間はないため {*} を外しても動きますが、念のため残しています。
    for article in root.findall(".//Article"):
        article_number = ""
        text_parts = []

        # 条番号 (ArticleCaptionがある場合はそれも考慮すると丁寧ですが、まずはTitleから)
        title_elem = article.find("ArticleTitle")
        if title_elem is not None and title_elem.text:
            article_number = title_elem.text.strip()

        # 本文の抽出
        # ParagraphSentence の直下のテキストだけでなく、中にある Sentence タグも取得
        for sentence in article.findall(".//Sentence"):
            if sentence.text:
                text_parts.append(sentence.text.strip())

        text = "\n".join(text_parts) # 改行を入れると読みやすくなります

        if article_number and text:
            results.append(
                Article(
                    law_name=law_name,
                    article_number=article_number,
                    text=text
                )
            )

    #print(f"SUCCESS: {law_name} - PARSED ARTICLES: {len(results)}")
    return results

# 実行テスト
if __name__ == "__main__":
    data = get_articles("刑法")
    # 最初の3件だけ表示
    for art in data["刑法"][:3]:
        print(f"[{art.article_number}] {art.text[:50]}...")