import json

with open('/Users/salahamran/Desktop/foodgram/data/ingredients.json', 'r',
          encoding='utf-8') as f:
    raw_ingredients = json.load(f)

fixture_data = []

for idx, item in enumerate(raw_ingredients, start=1):
    fixture_data.append({
        "model": "recipes.ingredient",
        "pk": idx,
        "fields": {
            "name": item["name"],
            "measurement_unit": item["measurement_unit"]
        }
    })

with open('data/ingredients_fixture.json', 'w', encoding='utf-8') as f:
    json.dump(fixture_data, f, ensure_ascii=False, indent=2)

print("Converted to fixture format: data/ingredients_fixture.json")
