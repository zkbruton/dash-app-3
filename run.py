import dash
import dash_table as dt
import dash_core_components as dcc
#import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
#import plotly.tools as tls
import plotly.graph_objects as go
#import plotly.express as px
import pandas as pd
import time
import numpy as np

"""
path1='Q:\\ERO Proposals\\15 SURFACE INFORMATION\\06 Workload Meetings\\SELL PRICE TRACKER - from May 2019.xlsx'
path2='Q:\\ERO Proposals\\15 SURFACE INFORMATION\\06 Workload Meetings\\SELL PRICE TRACKER cost history only.xlsx'
"""


#Sell Price Tracker Dataframe creation
path1='C:\\Users\\212774947\\Desktop\\SELL PRICE TRACKER - from May 2019.xlsx'
path2='C:\\Users\\212774947\\Desktop\\SELL PRICE TRACKER cost history only.xlsx'


x1 = pd.ExcelFile(path1)
x1_sheets = x1.sheet_names
x2 = pd.ExcelFile(path2)
x2_sheets = x2.sheet_names
df_spt=pd.DataFrame()
for i in x1_sheets:
    df_spt=df_spt.append(x1.parse(i),ignore_index=True, sort=True)
for i in x2_sheets:
    df_spt=df_spt.append(x2.parse(i),ignore_index=True, sort=True)
    
df_spt_copy=df_spt.copy() 
col=list(df_spt.columns)
  
df_spt['Quote'].fillna(df_spt['Quote No.'],inplace=True)
df_spt['Part Number'].fillna(df_spt['Part No.'],inplace=True)

df_spt = df_spt.drop([
           'Quote No.',
           'Part No.',
           'Unit Sell Price.1',
           'Al Hugayet',
           'Comment',
           'Comments',
           'Customer',
           'Client',
           'Feedback from Customer',
           'Margin excluding contingency & COC',
           'SPARES MARGINS - 2019'],
           axis=1)
df_spt[col[40]]=df_spt[col[40]].astype(str)
df_spt=df_spt[~df_spt[col[40]].str.contains('do not use', case=False)]
df_spt=df_spt[~df_spt[col[40]].str.contains('DON’T USE', case=False)]
df_spt=df_spt[df_spt.columns[~df_spt.columns.str.contains('Delivery')]]
df_spt=df_spt[df_spt.columns[~df_spt.columns.str.contains('Unnamed:')]]

df_spt[col[12]]=df_spt[col[12]].astype(str)
df_spt=df_spt[~df_spt[col[12]].str.contains('do not use', case=False)]
df_spt=df_spt[~df_spt[col[12]].str.contains('DON’T USE', case=False)]

conv_usd_gbp=.78
conv_cad_gbp=.59
df_spt['UNIT SELL PRICE CAD $']=df_spt['UNIT SELL PRICE CAD $']*conv_cad_gbp
df_spt['UNIT SELL PRICE USD $']=df_spt['UNIT SELL PRICE USD $']*conv_cad_gbp
df_spt[col[29]]=df_spt[col[29]]*conv_cad_gbp
df_spt[col[31]]=df_spt[col[31]]*conv_cad_gbp

df_spt['Unit Sell Price'].fillna(df_spt['Sell Price'],inplace=True)
df_spt['Unit Sell Price'].fillna(df_spt['UNIT SELL PRICE CAD $'],inplace=True)
df_spt['Unit Sell Price'].fillna(df_spt['UNIT SELL PRICE USD $'],inplace=True)
df_spt['Unit Sell Price'].fillna(df_spt[col[28]],inplace=True)
df_spt['Unit Sell Price'].fillna(df_spt[col[29]],inplace=True)
df_spt['Unit Sell Price'].fillna(df_spt[col[30]],inplace=True)
df_spt['Unit Sell Price'].fillna(df_spt[col[31]],inplace=True)
df_spt = df_spt.drop([
           'Sell Price',
           'UNIT SELL PRICE CAD $',
           'UNIT SELL PRICE USD $',
           col[28],
           col[12],
           col[29],
           col[30],
           col[31]],
           axis=1)

df_spt['Unit Cost Price'].fillna(df_spt['Unit Cost Price GBP'],inplace=True)
df_spt['Unit Cost Price'].fillna(df_spt['New Cost'],inplace=True)
df_spt['Unit Cost Price'].fillna(df_spt['COST'],inplace=True)
df_spt['Unit Cost Price'].fillna(df_spt[col[2]],inplace=True)
df_spt = df_spt.drop([
           'Unit Cost Price GBP',
           'New Cost',
           'COST',
           col[2]],
           axis=1)
df_spt=df_spt.dropna(subset=['Part Number'],axis=0)
df_spt['Part Number']=df_spt['Part Number'].astype(str)
df_spt=df_spt.reset_index(drop=True)
df_spt['Unit Cost Price']=pd.to_numeric(df_spt['Unit Cost Price'], errors='coerce')
df_spt['Unit Cost Price']=df_spt['Unit Cost Price'].round(decimals=2)
df_spt['Unit Sell Price']=pd.to_numeric(df_spt['Unit Sell Price'], errors='coerce')
df_spt['Unit Sell Price']=df_spt['Unit Sell Price'].round(decimals=2)
df_spt['CM']=(df_spt['Unit Sell Price']-df_spt['Unit Cost Price'])/df_spt['Unit Sell Price']
df_spt['CM']=df_spt['CM'].round(decimals=2)

new_col=['Part Number','Unit Cost Price','Unit Sell Price','CM','Date','Quote','Qty','Part description','Department']
df_spt=df_spt[new_col]
df_spt['Date']=pd.to_datetime(df_spt['Date'], unit='D')
df_spt=df_spt.drop(columns=['Part description','Department'])
df_spt=df_spt[['Part Number','Quote','Unit Cost Price','Unit Sell Price','CM','Date','Qty']]

#Cost Model Dataframe creation
#Repair
path3='C:\\Users\\212774947\\MyPythonScripts\\Total\\All_Repair.xlsx'
repair_data=pd.read_excel(path3, sheet_name='Full Data',index_col=0).reset_index(drop=True)
repair_data['PNs'] = repair_data.PNs.apply(lambda x: x[1:-1].split(','))

def PNcorrect(df):   
    for i in range(len(df.index)):
        a=df.at[i,'PNs']
#        if all(x == a[0] for x in a):
#            if len(a)>1:
#                a=a[0]
#                print(a)
        for ii in range(len(a)):
            if type(a) is not list:    
                a=[a]
            a[ii]=a[ii].replace("'","")
            a[ii]=a[ii].replace("\\xa0","")
            if "\\n" in a[ii]:
                a[ii]=a[ii].replace("\\n","")[:8]
            a[ii]=a[ii].replace(" ","")
         
            if "n/a" in a[ii].casefold():
                a[ii]=None      
            elif "graham" in a[ii].casefold():
                a[ii]=None 
            elif "hour" in a[ii].casefold():
                a[ii]=None
            elif "note" in a[ii].casefold():
                a[ii]=None 
            elif "workscope" in a[ii].casefold():
                a[ii]=None 
            elif "pn" in a[ii].casefold():
                a[ii]=None 
            elif "subcon" in a[ii].casefold():
                a[ii]=None
            elif "body" in a[ii].casefold():
                a[ii]=None
            elif "_REF" in a[ii].casefold():
                a[ii]=a[ii].replace("_REF","")

        a=list(filter(None, a))
        b=', '.join(a)
        df.at[i,'PNs']=b
    return df
repair_data=PNcorrect(repair_data)
for i in range(len(repair_data.index)):    
    q=pd.to_datetime(repair_data.at[i,'Date'],errors='coerce',utc=True)
    repair_data.at[i,'Date']=q
repair_data['Date']=repair_data['Date'].astype('datetime64[ns]')
repair_data['Date']=repair_data['Date'].values.astype('datetime64[D]')
repair_data=repair_data.drop(['Total Line Unit Sell','Total Line Ext Sell'],axis=1)
repair_data['Unit Cost']=repair_data['Total Unit Sell - No Spares']*(1-repair_data['Margin'])
repair_data_copy=repair_data.copy()
repair_data=repair_data.drop(columns=['Descriptions','Spares Description','Workscope','Material - Note','Bought Out - Note','Sub-Con - Note','Machining - Note','Fabrication - Note','Test & Assy - Note','Total Unit Sell - Spares'])
colls=['Material','Bought Out','Sub-Con','Machining','Fabrication','Test & Assy','Margin','Total Ext Sell - No Spares','Total Unit Sell - No Spares',
                 'Total Ext Sell - Spares','Total Unit Sell','Total Ext Sell','Unit Cost']
for ii in colls:
    xxy=repair_data[ii][np.isnan(pd.to_numeric(repair_data[ii],errors='coerce'))== False].apply(lambda x:round(x,2))
    for i in xxy.index:
        xxx=xxy.loc(axis=0)[i]
        repair_data.loc[i,ii]=xxx
new_colls=['PNs','Date','Quantity','Material','Bought Out','Sub-Con','Machining','Fabrication','Test & Assy','Margin','Unit Cost','Total Unit Sell - No Spares','Total Ext Sell - No Spares','Spare PNs','Total Ext Sell - Spares','Total Unit Sell','Total Ext Sell','Excel Name','Customer','Item Number']
repair_data=repair_data[new_colls]
repair_data['ident']=repair_data['Excel Name'].map(str) + ' - ' + repair_data['Item Number'].map(str)
repair_data.set_index('ident',inplace=True,drop=False)
repair_data=repair_data.drop(['ident'],axis=1)

repcol=repair_data.copy()
repcol=repcol.reset_index(drop=True)
#Shop Data
path4='C:\\Users\\212774947\\MyPythonScripts\\Total\\Hareness_Workload_1.xlsx'
#path4='Q:\\ERO Proposals\\15 SURFACE INFORMATION\\21 Commercial Dashboard\\Hareness_Workload_1.xlsx'

df_shop = pd.read_excel(path4)
col=list(df_shop.columns)
#df_shop_n=df_shop.dropna(subset=['Operation Desc'])

df_shop['Operation Desc']=df_shop['Operation Desc'].apply(str)
df_shop_si=df_shop[df_shop['Operation Desc'].str.contains('STRIP|VISUAL',case=False)]
df_shop_si = df_shop_si[df_shop_si['Operation Desc'].str.contains('POLISH',case=False) == False]
df_shop_si = df_shop_si.drop([col[0],col[1],col[23],col[2],
           col[3],col[5],col[6],col[7],col[8],col[11],col[12],col[15],col[19],col[24],
           col[32],col[33],col[34],col[35],col[36],col[37],col[38],col[39],col[40],col[41],
           col[42],col[44],col[45]
           ],
           axis=1)
df_shop_si=df_shop_si.reset_index(drop=True)

df_shop_2=df_shop.drop([col[0],col[1],col[23],col[2],col[7],col[8],col[10],
           col[3],col[5],col[6],col[7],col[8],col[11],col[12],col[15],col[19],col[24],
           col[32],col[33],col[34],col[35],col[36],col[37],col[38],col[39],col[40],col[41],
           col[42],col[44],col[45]
           ],
           axis=1)
df_shop_2=df_shop_2.reset_index(drop=True)

#New Build Dataframe creation
path5='C:\\Users\\212774947\\MyPythonScripts\\Total\\All_New_Build.xlsx'
nb_data=pd.read_excel(path5, sheet_name='Full Data',index_col=0).reset_index(drop=True)
nb_data['PNs'] = nb_data.PNs.apply(lambda x: x[1:-1].split(','))
nb_data=PNcorrect(nb_data)
for i in range(len(nb_data.index)):    
    q=pd.to_datetime(nb_data.at[i,'Date'],errors='coerce',utc=True)
    nb_data.at[i,'Date']=q
nb_data['Date']=nb_data['Date'].astype('datetime64[ns]')
nb_data['Date']=nb_data['Date'].values.astype('datetime64[D]')
nb_data=nb_data.drop(['Total Line Unit Sell','Total Line Ext Sell'],axis=1)
nb_data['Margin']=pd.to_numeric(nb_data['Margin'],errors='coerce')
nb_data=nb_data.dropna(subset=['Margin'])
nb_data['Unit Cost']=nb_data['Total Unit Sell - No Spares']*(1-nb_data['Margin'])
nb_data_copy=nb_data.copy()
nb_data=nb_data.drop(columns=['Descriptions','Spares Description','Workscope','Material - Note','Bought Out - Note','Sub-Con - Note','Machining - Note','Fabrication - Note','Test & Assy - Note','Total Unit Sell - Spares'])
colls=['Material','Bought Out','Sub-Con','Machining','Fabrication','Test & Assy','Margin','Total Ext Sell - No Spares','Total Unit Sell - No Spares',
                 'Total Ext Sell - Spares','Total Unit Sell','Total Ext Sell','Unit Cost']
for ii in colls:
    xxy=nb_data[ii][np.isnan(pd.to_numeric(nb_data[ii],errors='coerce'))== False].apply(lambda x:round(x,2))
    for i in xxy.index:
        xxx=xxy.loc(axis=0)[i]
        nb_data.loc[i,ii]=xxx
new_colls=['PNs','Date','Quantity','Material','Bought Out','Sub-Con','Machining','Fabrication','Test & Assy','Margin','Unit Cost','Total Unit Sell - No Spares','Total Ext Sell - No Spares','Spare PNs','Total Ext Sell - Spares','Total Unit Sell','Total Ext Sell','Excel Name','Customer','Item Number','Deal Machine ID']
nb_data=nb_data[new_colls]
nb_data['ident']=nb_data['Excel Name'].map(str) + ' - ' + nb_data['Item Number'].map(str)
nb_data.set_index('ident',inplace=True,drop=False)
nb_data=nb_data.drop(['ident'],axis=1)

nbcol=nb_data.copy()
nbcol=nbcol.reset_index(drop=True)

#Contract Dataframe
path6='C:\\Users\\212774947\\MyPythonScripts\\Dash\\Contract Info\\Contract_Data.xlsx'
con_data=pd.read_excel(path6, sheet_name='Full Data').reset_index(drop=True)
con_data['Part Number']=con_data['Part Number'].astype(str)

#Unique Customer Names
cust_names=pd.concat([con_data['Customer'],repair_data['Customer'],nb_data['Customer']]).unique()
cust_names=list(cust_names)
ll=[None]*len(cust_names)
for i in range(len(cust_names)):
    ll[i]={'label':cust_names[i],'value':cust_names[i]}

#Dash App creation
    
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets1 = ['https://codepen.io/zkbruton/pen/JjovEXN.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets1)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

colors = {
    'background': '#f1f1f1',
    'text': '#7FDBFF'
}

tabs_styles = {
    'height': '44px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'backgroundColor': '#f8f8f8'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'backgroundColor': '#f8f8f8',
    'fontWeight': 'bold'
}


    
#daterange = pd.date_range(start='2016',end='2020',freq='W')

def unixTimeMillis(dt):
    ''' Convert datetime to unix timestamp '''
    return int(time.mktime(dt.timetuple()))

def unixToDatetime(unix):
    ''' Convert unix timestamp to datetime. '''
    return pd.to_datetime(unix,unit='s')

def getMarks(begin, ending, Nth=40):
    ''' Returns the marks for labeling. 
        Every Nth value will be used.
    '''
    daterange = pd.date_range(start=begin,end=ending, freq='W')
    result = {}
    for i, date in enumerate(daterange):
        if(i%Nth == 1):
            # Append value to dict
            result[unixTimeMillis(date)] = str(date.strftime('%Y-%m-%d'))

    return result
                
app.layout = html.Div(style={'backgroundColor': colors['background'],'width':'100%','height':'100%','top':'0px','left':'0px','z-index':'1000','position':'sticky'}, children=[
    html.H4(children='Commercial Dashboard',style={'textAlign':'center'}),

    html.H5(children='''
        Dashboard for Pricing and Order Information from the UK
    ''',style={'textAlign':'center'}),
   
#    html.Br(),         
    
    html.Div([
        html.Div([
                html.Div([
                         html.H6('Filter by Part Number'),
                         dcc.Input(id='my-id', value='Type PN here', type='text'),
                         html.Div(id='my-div')
                         ],
                className='four columns',
                style={'textAlign':'center'}),                
#                style={'width': '48%', 'display': 'inline-block'}),
                
                html.Div([
                        html.H6('Filter by Customer'),
                        dcc.RadioItems(id='radio_1',
                                options=[
                                        {'label':'All','value':'All'},
                                        {'label':'Big 5','value':'Big 5'},
                                        {'label':'Customize','value':'Customize'}
                                        ],
                                value='All',
                                labelStyle={'display': 'inline-block', 'margin-right': 10}),
                        dcc.Dropdown(id='customer', 
                                     options=ll,
                                     multi=True,
                                     placeholder='Select Customers',
                                     style={'textAlign':'center'}),
#                        html.Div(id='customer-name')
                        ],
                className='eight columns',
                style={'textAlign':'center'})                
#                style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
                ],className='row'),
        
        
        
        html.Br(),
        html.Div(id='output-container-range-slider',style={'text-align':'center'}),
        html.Div([
                dcc.RangeSlider(
                    id='year_slider',
                    min = unixTimeMillis(df_spt['Date'].min()),
                    max = unixTimeMillis(df_spt['Date'].max()),
                    value = [unixTimeMillis(df_spt['Date'].min()),
                             unixTimeMillis(df_spt['Date'].max())],
                    marks=getMarks(df_spt['Date'].min(),
                                df_spt['Date'].max()))
                    ],
                    style={'margin-left':'auto','margin-right':'auto','width':'70%'}),
        html.Br(),
                ],
#                    style={'backgroundColor':'#f8f8f8','border-style':'solid','border-color':'rgb(211,211,211)','border-width':'2px','border-radius':'5px','padding':'5px'}),
                    style={'margin-left':'auto','margin-right':'auto','width':'80%','backgroundColor':'#f8f8f8','box-shadow':'2px 2px #c9c9c9','padding':'5px','border-radius':'5px'}),

    html.Br(),
    dcc.Tabs([
            dcc.Tab(label='Sell Price Tracker',value='tab1',children=[
                html.Div([
                    html.Div([html.H4('Table'),dt.DataTable(id='table',
#                                                   style_cell={'overflow': 'hidden','textOverflow': 'ellipsis','maxWidth': 0,},
                                                   style_table={'overflowX':'scroll'},
                                                   style_cell={'minWidth':'45px'},
                                                   style_header={'backgroundColor':'#f8f8f8','fontWeight':'bold'},
                                                   style_data_conditional=[{'if':{'row_index':'odd'},
                                                                            'backgroundColor':'#f8f8f8'}],
                                                   columns=[{"name": i, "id": i} for i in df_spt.columns],
#                                                   columns=['Part Number','Quote','Unit Cost Price','Unit Sell Price','CM','Date','Qty'],
                                                   style_as_list_view=True,
                                                   data=df_spt.head(10).to_dict('records'))
                            ], style={'text-align':'center'}, className='six columns'),
                    html.Div([html.H4('Graph'),dcc.Graph(id='g1', figure={})], className='six columns'),
                        ],style={'text-align':'center','padding': '8px'},className="row"),
                    ],style=tab_style,selected_style=tab_selected_style),
            dcc.Tab(label='Cost Model Data',value='tab2',children=[
                    dcc.Tabs(id='subtabsCM',value='subtabsSM',children=[  
                        dcc.Tab(label='Repair Work',
                                children=[html.Div([
                                            html.Div([html.H4('Table'),
                                                      dt.DataTable(id='table_repair',
                #                                                   style_cell={'overflow': 'hidden','textOverflow': 'ellipsis','maxWidth': 0,},
                                                                   style_table={'overflowX':'scroll'},
                                                                   row_selectable="single",
                                                                   selected_rows=[],
                                                                   style_header={'backgroundColor':'#f8f8f8','fontWeight':'bold'},
                                                                   style_data_conditional=[{'if':{'row_index':'odd'},
                                                                                            'backgroundColor':'#f8f8f8'}],
                                                                   style_cell={'minWidth':'45px'},
                                                                   columns=[{"name": i, "id": i} for i in repcol.columns],
#                                                                   style_as_list_view=True,
                                                                   data=repair_data.head(10).to_dict('records'))
                                                    ])],style={'padding':'8px'}),
                                          html.Div([
                                            html.Div([html.H4('Graph'),dcc.Graph(id='g_repair', figure={})], className='six columns'),
                                            html.Div([html.H4('Donut Chart'),dcc.Graph(id='g_donut_repair', figure={})], className='six columns'),
                                                ],style={'padding':'8px'},className="row"),
                                            ],style=tab_style,selected_style=tab_selected_style
                                ),
                        dcc.Tab(label='New Build',
                                children=[html.Div([
                                            html.Div([html.H4('Table'),
                                                      dt.DataTable(id='table_nb',
                #                                                   style_cell={'overflow': 'hidden','textOverflow': 'ellipsis','maxWidth': 0,},
                                                                   style_table={'overflowX':'scroll'},
                                                                   row_selectable="single",
                                                                   selected_rows=[],
                                                                   style_header={'backgroundColor':'#f8f8f8','fontWeight':'bold'},
                                                                   style_data_conditional=[{'if':{'row_index':'odd'},
                                                                                            'backgroundColor':'#f8f8f8'}],
                                                                   style_cell={'minWidth':'45px'},
                                                                   columns=[{"name": i, "id": i} for i in nb_data.columns],
                                                                   data=nb_data.head(10).to_dict('records'))
                                                    ])],style={'padding':'8px'}),
                                          html.Div([
                                            html.Div([html.H4('Graph'),dcc.Graph(id='g_nb', figure={})], className='six columns'),
                                            html.Div([html.H4('Donut Chart'),dcc.Graph(id='g_donut_nb', figure={})], className='six columns'),
                                                ],style={'padding':'8px'},className="row"),
                                            ],style=tab_style,selected_style=tab_selected_style
                                ),
                        ]),
                ],style=tab_style,selected_style=tab_selected_style),
            dcc.Tab(label='Contract Information',value='tab3',children=[
                    html.Div([html.H4('Table'),
                              dt.DataTable(id='table_contract',
                                           style_table={'overflowX':'scroll'},
                                           row_selectable="single",
                                           selected_rows=[],
                                           style_header={'backgroundColor':'#f8f8f8','fontWeight':'bold'},
                                           style_data_conditional=[{'if':{'row_index':'odd'},
                                                                    'backgroundColor':'#f8f8f8'}],
                                           style_cell={'minWidth':'45px'},
                                           columns=[{"name": i, "id": i} for i in con_data.columns],
                                           data=con_data.head(10).to_dict('records'))
                            ],style={'padding':'8px'})
                    ],
                    style=tab_style,selected_style=tab_selected_style),
            ]),



#    dcc.Tabs(id="tabs", value='tab1', children=[
#            dcc.Tab(label='Tab One', value='tab1',
#                    children=[dcc.Tabs(id="subtabs", value="subtab1",
#                        children = [dcc.Tab(label='Sub Tab1', value="subtab1")])]),
#            dcc.Tab(label='Tab Two', value='tab2'),
#            dcc.Tab(label='Tab Three', value='tab3'),
#        ]),
    html.Div(id='tabs-content')
])
##Callback for Customer Selection
@app.callback(
    Output(component_id='customer', component_property='value'),
    [Input(component_id='radio_1', component_property='value')]
)    
def update_cust_name(value):
    if value == 'All':
        return cust_names
    elif value == 'Big 5':
        return ['TOTAL E&P','CNOOC prev Nexen','Chevron now Ithaca','Chrysaor prev COP','Apache']
    else:
        return

    
##Callbacks for Sell Price Tracker
@app.callback(
    dash.dependencies.Output('output-container-range-slider', 'children'),
    [dash.dependencies.Input('year_slider', 'value')])
def update_output(value):
    value=unixToDatetime(value)
    value1="start date of "+value[0].strftime("%Y-%b-%d")+" and end date of "+value[1].strftime("%Y-%b-%d")
    return 'Selected {}.'.format(value1)

@app.callback(
    Output(component_id='my-div', component_property='children'),
    [Input(component_id='my-id', component_property='value')]
)
def update_output_div(input_value):
    return 'PN entered is "{}"'.format(input_value)

#@app.callback(
#    Output(component_id='customer-name', component_property='children'),
#    [Input(component_id='customer', component_property='value')]
#)
#def update_output_cust(input_value):
#    return 'Customer Name entered is "{}"'.format(input_value)

@app.callback(
    Output(component_id='table', component_property='data'),
    [Input(component_id='my-id', component_property='value'),
     Input(component_id='year_slider', component_property='value')]
)
def update_gen_table(input_value,date_span):
    input_value=str(input_value)
    date_span=pd.to_datetime(date_span,unit='s')
    df_spt1=df_spt[(df_spt['Date'] >= date_span[0]) & (df_spt['Date'] <= date_span[1])]
    df_spt1['Date'] = df_spt1['Date'].dt.date
    return df_spt1[df_spt1['Part Number']==input_value].to_dict('records')
    
@app.callback(
    Output(component_id='g1', component_property='figure'),
    [Input(component_id='my-id', component_property='value'),
     Input(component_id='year_slider', component_property='value')]
)
def update_graph_spt(input_value,date_span):
    input_value=str(input_value)
    date_span=pd.to_datetime(date_span,unit='s')
    df_spt1=df_spt[(df_spt['Date'] >= date_span[0]) & (df_spt['Date'] <= date_span[1])]
    df=df_spt1[df_spt1['Part Number']==input_value]
    df=df.reset_index()
    text_hold=[None]*len(df.index)
    for i in range(len(df.index)):
        text_hold[i]='Quote = '+str(df.at[i,'Quote'])+'<br>Unit Cost Price = '+str(df.at[i,'Unit Cost Price'])+'<br>Unit Sell Price = '+str(df.at[i,'Unit Sell Price'])+'<br>Contribution Margin = '+str(df.at[i,'CM'])
    maxx=df['CM'].max()
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'],y=df['Unit Cost Price'],mode='markers',marker=dict(size=df['CM'],sizemode='area',sizeref=2.*maxx/(40.**2),sizemin=4),name='Unit Cost Price',text=text_hold))
    fig.layout.plot_bgcolor='#f8f8f8'
    fig.layout.paper_bgcolor='#f8f8f8'
    fig.update_layout(xaxis_title='Date',yaxis_title='Unit Cost Price')
    fig.update_layout(title={'text':'Sell Price Tracker','y':0.9,'x':0.5,'xanchor':'center','yanchor':'top'},font=dict(size=14))    
    fig.update_xaxes(showline=True,showgrid=True, gridwidth=1, gridcolor='#e4e4e4',linecolor='#c9c9c9',zerolinecolor='#e4e4e4')
    fig.update_yaxes(showline=True,showgrid=True, gridwidth=1, gridcolor='#e4e4e4',linecolor='#c9c9c9',zerolinecolor='#e4e4e4')
    return fig

@app.callback(
    Output(component_id='table_repair', component_property='data'),
    [Input(component_id='my-id', component_property='value'),
     Input(component_id='year_slider', component_property='value'),
     Input(component_id='customer', component_property='value')]
)
def update_rep_table(input_value,date_span,cust_name):
    if not cust_name:
        cust_name=cust_names
    input_value=str(input_value)
    date_span=pd.to_datetime(date_span,unit='s')
    repair_data1=repair_data[(repair_data['Date'] >= date_span[0]) & (repair_data['Date'] <= date_span[1])]
    repair_data1=repair_data1[repair_data1['Customer'].isin(cust_name)]
    return repair_data1[repair_data1['PNs']==input_value].to_dict('records')
    
@app.callback(
    Output(component_id='g_repair', component_property='figure'),
    [Input(component_id='my-id', component_property='value'),
     Input(component_id='year_slider', component_property='value'),
     Input('table_repair', 'selected_rows'),
     Input(component_id='customer', component_property='value')]
)
def update_graph_rep(input_value,date_span,selected_rows,cust_name):
    input_value=str(input_value)
    if not selected_rows:
        selected_rows=[1000]
    selected_rows=''.join(str(v) for v in selected_rows)
    selected_rows=int(selected_rows)
    date_span=pd.to_datetime(date_span,unit='s')
    repair_data1=repair_data[(repair_data['Date'] >= date_span[0]) & (repair_data['Date'] <= date_span[1])]
    if not cust_name:
        cust_name=cust_names
    repair_data1=repair_data1[repair_data1['Customer'].isin(cust_name)]
    df_rep=repair_data1[repair_data1['PNs']==input_value]
    df_rep['Text']='Quote = '+df_rep['Excel Name'].map(str)+'<br>Unit Cost Price = '+df_rep['Unit Cost'].map(str)+'<br>Unit Sell Price = '+df_rep['Total Unit Sell - No Spares'].map(str)+'<br>Contribution Margin = '+df_rep['Margin'].map(str)
    text_hold=df_rep['Text'].tolist()
    maxx=df_rep['Margin'].max()
    colage=[1]*len(df_rep['Date'])
    if selected_rows < len(df_rep['Date']):
        colage=[1]*len(df_rep['Date'])
        colage[selected_rows]=2
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=df_rep['Date'],y=df_rep['Unit Cost'],mode='markers',marker=dict(size=df_rep['Margin'],sizemode='area',sizeref=2.*maxx/(40.**2),sizemin=4,color=colage),name='Unit Cost',text=text_hold))
    fig.layout.plot_bgcolor='#f8f8f8'
    fig.layout.paper_bgcolor='#f8f8f8'
    fig.update_layout(xaxis_title='Date',yaxis_title='Unit Cost Price')
    fig.update_layout(title={'text':'Repair Cost Models','y':0.9,'x':0.5,'xanchor':'center','yanchor':'top'},font=dict(size=14))    
    fig.update_xaxes(showline=True,showgrid=True, gridwidth=1, gridcolor='#e4e4e4',linecolor='#c9c9c9',zerolinecolor='#e4e4e4')
    fig.update_yaxes(showline=True,showgrid=True, gridwidth=1, gridcolor='#e4e4e4',linecolor='#c9c9c9',zerolinecolor='#e4e4e4')
    return fig    

@app.callback(
    Output('g_donut_repair', 'figure'),
    [Input(component_id='my-id', component_property='value'),
     Input(component_id='year_slider', component_property='value'),
     Input('table_repair', 'selected_rows'),
     Input(component_id='customer', component_property='value')])
def update_donut_rep(input_value,date_span,selected_rows,cust_name):
    input_value=str(input_value)
    if not selected_rows:
        selected_rows=[0]
    selected_rows=''.join(str(v) for v in selected_rows)
    selected_rows=int(selected_rows)
    date_span=pd.to_datetime(date_span,unit='s')
    repair_data2=repair_data_copy[(repair_data_copy['Date'] >= date_span[0]) & (repair_data_copy['Date'] <= date_span[1])].reset_index(drop=True)
    if not cust_name:
        cust_name=cust_names
    repair_data2=repair_data2[repair_data2['Customer'].isin(cust_name)]
    hold=repair_data2['PNs']==input_value
    rd2=repair_data2[hold].reset_index(drop=True)
    if len(rd2.index)==0:
        x1,x2,x3,x4,x5,x6=1,1,1,1,1,1
        z1=z2=z3=z4=z5=z6='Placement Value'
    else:
        x1=rd2.loc[selected_rows,'Material']
        x2=rd2.loc[selected_rows,'Bought Out']
        x3=rd2.loc[selected_rows,'Sub-Con']
        x4=rd2.loc[selected_rows,'Machining']
        x5=rd2.loc[selected_rows,'Fabrication']
        x6=rd2.loc[selected_rows,'Test & Assy']
        z1=rd2.loc[selected_rows,'Material - Note']
        z2=rd2.loc[selected_rows,'Bought Out - Note']
        z3=rd2.loc[selected_rows,'Sub-Con - Note']
        z4=rd2.loc[selected_rows,'Machining - Note']
        z5=rd2.loc[selected_rows,'Fabrication - Note']
        z6=rd2.loc[selected_rows,'Test & Assy - Note']
    z=[z1,z2,z3,z4,z5,z6]
    c=':'
    for i in range(len(z)):
        zz=str(z[i])
        foo=[pos for pos, char in enumerate(zz) if char == c]
        if len(foo)>1:
            foo1=foo[1]+1
            z[i]=z[i][:foo1]+'<br>'+z[i][foo1:]
    fig=go.Figure(data=[go.Pie(labels=['Material','Bought Out','Sub-Con','Machining','Fabrication','Test & Assy'], values=[x1,x2,x3,x4,x5,x6],hole=.3,hovertext=z,hoverinfo="text")])
    fig.layout.plot_bgcolor='#f8f8f8'
    fig.layout.paper_bgcolor='#f8f8f8'
    fig.update_layout(title={'text':'Cost Breakdown','y':0.9,'x':0.5,'xanchor':'center','yanchor':'top'},font=dict(size=14)) 
    return fig

#New Build Tab    
@app.callback(
    Output(component_id='table_nb', component_property='data'),
    [Input(component_id='my-id', component_property='value'),
     Input(component_id='year_slider', component_property='value'),
     Input(component_id='customer', component_property='value')]
)
def update_nb_table(input_value,date_span,cust_name):
    input_value=str(input_value)
    date_span=pd.to_datetime(date_span,unit='s')
    nb_data1=nb_data[(nb_data['Date'] >= date_span[0]) & (nb_data['Date'] <= date_span[1])]
    if not cust_name:
        cust_name=cust_names
    nb_data1=nb_data1[nb_data1['Customer'].isin(cust_name)]
    return nb_data1[nb_data1['PNs']==input_value].to_dict('records')
   
@app.callback(
    Output(component_id='g_nb', component_property='figure'),
    [Input(component_id='my-id', component_property='value'),
     Input(component_id='year_slider', component_property='value'),
     Input('table_nb', 'selected_rows'),
     Input(component_id='customer', component_property='value')]
)
def update_graph_nb(input_value,date_span,selected_rows,cust_name):
    input_value=str(input_value)
    if not selected_rows:
        selected_rows=[1000]
    selected_rows=''.join(str(v) for v in selected_rows)
    selected_rows=int(selected_rows)
    date_span=pd.to_datetime(date_span,unit='s')
    nb_data1=nb_data[(nb_data['Date'] >= date_span[0]) & (nb_data['Date'] <= date_span[1])]
    df_nb=nb_data1[nb_data1['PNs']==input_value]
    if not cust_name:
        cust_name=cust_names
    df_nb=df_nb[df_nb['Customer'].isin(cust_name)]
    df_nb['Text']='Quote = '+df_nb['Excel Name'].map(str)+'<br>Unit Cost Price = '+df_nb['Unit Cost'].map(str)+'<br>Unit Sell Price = '+df_nb['Total Unit Sell - No Spares'].map(str)+'<br>Contribution Margin = '+df_nb['Margin'].map(str)
    text_hold=df_nb['Text'].tolist()
    maxx=df_nb['Margin'].max()
    colage=[1]*len(df_nb['Date'])
    if selected_rows < len(df_nb['Date']):
        colage=[1]*len(df_nb['Date'])
        colage[selected_rows]=2
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=df_nb['Date'],y=df_nb['Unit Cost'],mode='markers',marker=dict(size=df_nb['Margin'],sizemode='area',sizeref=2.*maxx/(40.**2),sizemin=4,color=colage),name='Unit Cost',text=text_hold))
    fig.layout.plot_bgcolor='#f8f8f8'
    fig.layout.paper_bgcolor='#f8f8f8'
    fig.update_layout(xaxis_title='Date',yaxis_title='Unit Cost Price')
    fig.update_layout(title={'text':'New Build Cost Models','y':0.9,'x':0.5,'xanchor':'center','yanchor':'top'},font=dict(size=14))    
    fig.update_xaxes(showline=True,showgrid=True, gridwidth=1, gridcolor='#e4e4e4',linecolor='#c9c9c9',zerolinecolor='#e4e4e4')
    fig.update_yaxes(showline=True,showgrid=True, gridwidth=1, gridcolor='#e4e4e4',linecolor='#c9c9c9',zerolinecolor='#e4e4e4')
    return fig

@app.callback(
    Output('g_donut_nb', 'figure'),
    [Input(component_id='my-id', component_property='value'),
     Input(component_id='year_slider', component_property='value'),
     Input('table_nb', 'selected_rows'),
     Input(component_id='customer', component_property='value')])
def update_donut_gb(input_value,date_span,selected_rows,cust_name):
    input_value=str(input_value)
    if not selected_rows:
        selected_rows=[0]
    selected_rows=''.join(str(v) for v in selected_rows)
    selected_rows=int(selected_rows)
    date_span=pd.to_datetime(date_span,unit='s')
    nb_data2=nb_data_copy[(nb_data_copy['Date'] >= date_span[0]) & (nb_data_copy['Date'] <= date_span[1])].reset_index(drop=True)
    if not cust_name:
        cust_name=cust_names
    nb_data2=nb_data2[nb_data2['Customer'].isin(cust_name)]
    hold=nb_data2['PNs']==input_value
    nbd2=nb_data2[hold].reset_index(drop=True)
    if len(nbd2.index)==0:
        x1,x2,x3,x4,x5,x6=1,1,1,1,1,1
        z1=z2=z3=z4=z5=z6='Placement Value'
    else:
        x1=nbd2.loc[selected_rows,'Material']
        x2=nbd2.loc[selected_rows,'Bought Out']
        x3=nbd2.loc[selected_rows,'Sub-Con']
        x4=nbd2.loc[selected_rows,'Machining']
        x5=nbd2.loc[selected_rows,'Fabrication']
        x6=nbd2.loc[selected_rows,'Test & Assy']
        z1=nbd2.loc[selected_rows,'Material - Note']
        z2=nbd2.loc[selected_rows,'Bought Out - Note']
        z3=nbd2.loc[selected_rows,'Sub-Con - Note']
        z4=nbd2.loc[selected_rows,'Machining - Note']
        z5=nbd2.loc[selected_rows,'Fabrication - Note']
        z6=nbd2.loc[selected_rows,'Test & Assy - Note']
    z=[z1,z2,z3,z4,z5,z6]
    fig=go.Figure(data=[go.Pie(labels=['Material','Bought Out','Sub-Con','Machining','Fabrication','Test & Assy'], values=[x1,x2,x3,x4,x5,x6],hole=.3,hovertext=z,hoverinfo="text")])
    fig.layout.plot_bgcolor='#f8f8f8'
    fig.layout.paper_bgcolor='#f8f8f8'
    fig.update_layout(title={'text':'Cost Breakdown','y':0.9,'x':0.5,'xanchor':'center','yanchor':'top'},font=dict(size=14))       
    return fig

#Contract Tab    
@app.callback(
    Output(component_id='table_contract', component_property='data'),
    [Input(component_id='my-id', component_property='value'),
     Input(component_id='customer', component_property='value')]
)
def update_con_table(input_value,cust_name):
    input_value=str(input_value)
    if not cust_name:
        cust_name=cust_names
    con_data1=con_data[con_data['Customer'].isin(cust_name)]
    return con_data1[con_data1['Part Number']==input_value].to_dict('records')



if __name__ == '__main__':
    app.run_server(debug=True)
