import sys
from dataclasses import dataclass 

import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from source.exception import CustomException
from source.logger import logging
import os
from source.utils import save_object


@dataclass
class DataTransformationConfig:
    preprocessing_obj_file_path = os.path.join("artifacts","preprocessor.pkl")

class DataTransformation:
    def __init__(self):
        self.data_transformation_config = DataTransformationConfig()

    def get_data_transformer_object(self):
        '''
        This function is responsible for data transfromation
        '''
        try:
            numeric_features = ['reading_score', 'writing_score']
            categorical_features = ['gender', 
                                    'race_ethnicity', 
                                    'parental_level_of_education', 
                                    'lunch', 
                                    'test_preparation_course']

            num_pipeline = Pipeline(
                steps = [
                    ("imputer", SimpleImputer(strategy= "median")),
                    ("scaler", StandardScaler())
                ]
            )

            cat_pipeline = Pipeline(
                steps= [
                    ("imputer", SimpleImputer(strategy= "most_frequent")),
                    ("one_hot_encoding", OneHotEncoder()),
                    ("scaler", StandardScaler(with_mean= False))
                ]
            )

            logging.info(f"Categorical columns: {categorical_features}")
            logging.info(f"Numerical columns: {numeric_features}")

            preprocessor = ColumnTransformer(
                [
                    ("num_pipeline", num_pipeline, numeric_features),
                    ("cat_pipeline", cat_pipeline, categorical_features)
                ]
            )

            return preprocessor
        except Exception as e:
            raise CustomException(e, sys)
        
    def initiate_data_transformation(self, train_path, test_path):
        try:
            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)

            logging.info("Read train and test data completed..")

            logging.info("Obtaining preprocessing object..")

            preprocessing_obj = self.get_data_transformer_object()

            target_column_name = "math_score"

            numeric_features = ['reading_score', 'writing_score']

            input_feature_train_df = train_df.drop(columns = [target_column_name])
            target_feature_train_df = train_df[target_column_name]
            
            input_feature_test_df = test_df.drop(columns = [target_column_name])
            target_feature_test_df = test_df[target_column_name]

            logging.info(f"Applying preprocessing object on training dataframe and testing dataframe.")

            input_feature_train_arr = preprocessing_obj.fit_transform(input_feature_train_df)
            input_feature_test_arr = preprocessing_obj.transform(input_feature_test_df)

            #combinigs two arrays
            train_arr = np.c_[input_feature_train_arr, np.array(target_feature_train_df)]
            test_arr = np.c_[input_feature_test_arr, np.array(target_feature_test_df)]

            logging.info(f"Saved preprocessing object.")

            save_object(

                file_path = self.data_transformation_config.preprocessing_obj_file_path,
                obj = preprocessing_obj
            )

            return (
                train_arr,
                test_arr,
                self.data_transformation_config.preprocessing_obj_file_path
            )

        except Exception as e:
            raise CustomException(e, sys)