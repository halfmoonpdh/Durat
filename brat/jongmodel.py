#-*- encoding=utf-8 -*-

import os
import pickle
from konlpy.tag import Kkma

def text_refine(text):
    '''
    텍스트 데이터를 정제하여 사용할수 있도록 하기 위해 존제
    text는 String 타입이여야함
    '''
    kkma = Kkma()
    data =  ' '.join(kkma.morphs(text))

    return data

def model_predict(data):
    pickle_model = os.path.join(os.path.dirname(__file__), 'model.pickle')
    with open(pickle_model, 'rb') as f:
        while True:
            try:
                model = pickle.load(f)
            except(EOFError):
                break

    data = text_refine(data)

    return model.predict([data])[0]  # 모델을 학습한후 결과 반환


if __name__ == '__main__':
    '''
    작동 예제
    '''
    print(model_predict('본 연구에서는 연료전지에의 응용을 위한 저가격의 무산소, 상온동작 가능한 센서구조를 설계, 제작하고 특성을 평가하였다.'))
