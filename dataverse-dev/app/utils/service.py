import http3
import pandas as pd
from app.models.vehicle_details import SubVariant, Variant


# method is used for valid id in bulk upload of data:
def validate_id(model_dict: dict, x: str):
    try:
        return model_dict.get(x.lower())
    except:
        return


# This method is only used when ex-showroom-price template is downloaded: for handling the sub-variant id
async def write_sub_variant_into_csv(loc):
    sub_variant = await SubVariant.fetch_all()
    sub_variant_dict = {"id": [], "color": [], "tone": [], "variant_id": []}

    for item in sub_variant:
        sub_variant_dict["id"].append(item.id)
        sub_variant_dict["color"].append(item.color)
        sub_variant_dict["tone"].append(item.tone)
        variant_dict = await Variant.fetch(key=item.variant_id)
        sub_variant_dict["variant_id"].append(variant_dict.name)
    df = pd.DataFrame(sub_variant_dict)
    updated_df = pd.read_csv(loc)
    updated_df["id"] = df["id"]
    updated_df["color"] = df["color"]
    updated_df["tone"] = df["tone"]
    updated_df["variant_info"] = df["variant_id"]
    updated_df.to_csv(loc, index=False, header=True)
    return loc


async def call_auth_api(url: str):
    client = http3.AsyncClient()
    get_model_data = await client.get(url)
    return get_model_data.json()
