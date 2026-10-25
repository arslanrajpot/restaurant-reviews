import pandas as pd
from restaurants.repository import update_restaurant


def populate_calculations():
    csv_file_path = "csv/merged_data_new.csv"
    df = pd.read_csv(csv_file_path)

    # Select and clean columns
    df = df[['Restaurant Name', 'Total Rating', 'Overall Rating', 'Food Rating', 'Service Rating', 'Ambience Rating']]
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    df.fillna(0, inplace=True)

    # Convert ratings to float
    rating_cols = ['total_rating', 'overall_rating', 'food_rating', 'service_rating', 'ambience_rating']
    for col in rating_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Categorize star levels based on overall_rating
    df['five_stars'] = ((df['overall_rating'] >= 4.5) & (df['overall_rating'] <= 5)).astype(int)
    df['four_stars'] = ((df['overall_rating'] >= 3.5) & (df['overall_rating'] < 4.5)).astype(int)
    df['three_stars'] = ((df['overall_rating'] >= 2.5) & (df['overall_rating'] < 3.5)).astype(int)
    df['two_stars'] = ((df['overall_rating'] >= 1.5) & (df['overall_rating'] < 2.5)).astype(int)
    df['one_stars'] = ((df['overall_rating'] >= 0) & (df['overall_rating'] < 1.5)).astype(int)

    # Total number of reviews
    df['total_review_count'] = 1

    # Group by restaurant and aggregate
    grouped = df.groupby('restaurant_name', as_index=False).agg({
        'total_rating': 'mean',
        'overall_rating': 'mean',
        'food_rating': 'mean',
        'service_rating': 'mean',
        'ambience_rating': 'mean',
        'five_stars': 'sum',
        'four_stars': 'sum',
        'three_stars': 'sum',
        'two_stars': 'sum',
        'one_stars': 'sum',
        'total_review_count': 'sum'
    })

    # Round rating columns
    grouped[['total_rating', 'overall_rating', 'food_rating', 'service_rating', 'ambience_rating']] = grouped[
        ['total_rating', 'overall_rating', 'food_rating', 'service_rating', 'ambience_rating']
    ].round(1)

    # Final data
    full_df = grouped.to_dict(orient='records')
    update_restaurant(full_df)


if __name__ == "__main__":
    populate_calculations()
