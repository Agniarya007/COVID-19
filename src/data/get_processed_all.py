import numpy as np
from sklearn import linear_model
reg = linear_model.LinearRegression(fit_intercept=True)
import pandas as pd
import os
from scipy import signal

def doubling_time_via_regression(in_array):
    ''' Use a linear regression to approximate the doubling rate   '''

    y = np.array(in_array)
    X = np.arange(len(y)).reshape(-1, 1)

    #assert len(in_array)==3
    reg.fit(X,y)
    intercept=reg.intercept_
    slope=reg.coef_

    return intercept/slope


def savgol_filt(df_input,column='confirmed',window=5):
    ''' Savgol Filter which can be used in groupby apply function (data structure kept)  '''

        
  
    degree=1
    df_result=df_input

    filter_in=df_input[column].fillna(0) # attention with the neutral element here

    result=signal.savgol_filter(np.array(filter_in),
                           window, # window size used for filtering
                           1)
    df_result[str(column+'_filtered')]=result
    return df_result

def roll_regr(df_input,col='confirmed'):
    ''' Rolling Regression to approximate the doubling time' 
    '''

    days_back=5
    result=df_input[col].rolling(
                window=days_back,
                min_periods=3).apply(doubling_time_via_regression,raw=False)



    return result




def calc_filt_data(df_input,filter_on='confirmed'):
    '''  Calculate savgol filter and return merged data frame

    '''

    must_contain=set(['state','country',filter_on])
    assert must_contain.issubset(set(df_input.columns)), ' Erro in calc_filt_data not all columns in data frame'

    df_output=df_input.copy() 

    pd_filtered_result=df_output[['state','country',filter_on]].groupby(['state','country']).apply(savgol_filt)  


    df_output=pd.merge(df_output,pd_filtered_result[[str(filter_on+'_filtered')]],left_index=True,right_index=True,how='left')
    return df_output.copy()





def calc_doubling_rate(df_input,filter_on='confirmed'):
    ''' Calculate approximated doubling rate and return merged data frame
        the result will be joined as a new column on the input data frame
    '''

    must_contain=set(['state','country',filter_on])
    assert must_contain.issubset(set(df_input.columns)), ' Error in calc_filt_data not all columns in data frame'


    pd_DR_result= df_input.groupby(['state','country']).apply(roll_regr,filter_on).reset_index()

    pd_DR_result=pd_DR_result.rename(columns={filter_on:filter_on+'_DR',
                             'level_2':'index'})

    df_output=pd.merge(df_input,pd_DR_result[['index',str(filter_on+'_DR')]],left_index=True,right_on=['index'],how='left')
    df_output=df_output.drop(columns=['index'])


    return df_output



def processed_result_all():
    dir_path=os.path.join(os.path.dirname(__file__),r'..\..\data\raw\COVID-19')
    csv_DIRpath=os.path.join(dir_path,r'..\..\processed' )
    csv1_path=os.path.join(csv_DIRpath,'COVID_relational_confirmed.csv')
    csv2_path=os.path.join(csv_DIRpath,'COVID_final_set.csv')
    pd_JH_data=pd.read_csv(csv1_path,sep=';',parse_dates=[0])
    pd_JH_data=pd_JH_data.sort_values('date',ascending=True).copy()

 

    pd_result_larg=calc_filt_data(pd_JH_data)
    pd_result_larg=calc_doubling_rate(pd_result_larg)
    pd_result_larg=calc_doubling_rate(pd_result_larg,'confirmed_filtered')


    mask=pd_result_larg['confirmed']>100
    pd_result_larg['confirmed_filtered_DR']=pd_result_larg['confirmed_filtered_DR'].where(mask, other=np.NaN)
    pd_result_larg.to_csv(csv2_path,sep=';',index=False)
