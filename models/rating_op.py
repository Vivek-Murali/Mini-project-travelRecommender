import pandas as pd


class Rating(object):

    @staticmethod
    def rating(df1, df):
        rating_count = pd.DataFrame(df1, columns=['place_id', 'no_of_rating'])
        rating_count = rating_count.sort_values('no_of_rating', ascending=False)
        rating_count1 = rating_count['place_id'][:10]
        rating_count1 = rating_count1.values.tolist()
        most_rated = pd.DataFrame(rating_count1, index=np.arange(10), columns=['place_id'])
        details = pd.merge(most_rated, df, on='place_id')
        rating = pd.DataFrame(df1.groupby('place_id')['no_of_rating'].mean())
        rating.sort_values('no_of_rating', ascending=False)
        rating_pivot = pd.pivot_table(data=df1, values='user_rating', index='user_id', columns='place_id')
        correlation_mat = rating_pivot.corr(method='pearson')
        oneman = rating_pivot[rating_count1[1]]
        similar_to = rating_pivot.corrwith(oneman)
        corr_oneman = pd.DataFrame(similar_to, columns=['PearsonR'])
        oneman_sum = corr_oneman.join(rating)
        oneman_sum1 = oneman_sum.sort_values('PearsonR', ascending=False)
        oneman_sum2 = oneman_sum1.index.values.tolist()
        place_coor = pd.DataFrame(oneman_sum2, index=np.arange(176), columns=['place_id'])
        sumarry = pd.merge(place_coor, df, on='place_id')
        places = sumarry[:10]
        return places
