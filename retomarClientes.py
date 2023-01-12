import pandas as pd
import numpy as np
import re
from whatsapiRetoma import whatsappSender

numbersSents = []

with open ('clientWhatsappSent.txt', 'rt') as myfile:
    for myline in myfile:
        number = myline.replace(' ', '').replace('\n', '')
        numbersSents.append(number)

#Open the txt file hwere are the saved numbers
opener = open(r'clientWhatsappSent.txt', 'a+')

#Save the numbers automatically to the file 
def numberSaver(theElement):
    nuevo = theElement.replace(' ', '')
    opener.write(nuevo)
    opener.write('\n')

#Read the principal database
df = pd.read_excel('retomarclientes.xlsx')


columns_mine = ['MAPFRE', 'AXA', 'ALLIANZ', 'ESTADO', 'HDI', 'LIBERTY', 'EQUIDAD', 'ZURICHC', 'SBS',  'BOLIVAR']

#Data cleaning
for col in columns_mine:

  for i in df[col]:

    if type(i) == str:
      if re.findall(r"^\w+", i):
        df[col] = df[col].replace(to_replace = i, value = 0)
      else:
        nuevo = i.replace('$', '')
        ultimo =nuevo.replace('.', '').replace(',', '')
        df[col] = df[col].replace(to_replace = i, value = ultimo)
        if i == '0' or '0.0':
          df[col] = df[col].replace(to_replace = '0', value = 10000000000)
        else: 
          pass

    else: 
      pass

for columna in columns_mine:
  df[columna] = df[columna].astype('float64')

  for numero in df[columna]:
    if numero == 0 or 0.0:
      df[columna] = df[columna].replace(to_replace = 0, value =1000000000)
      df[columna] = df[columna].replace(to_replace = 0.0, value =1000000000)




#Set the format of the cell with the code contry
df['CELULAR'] = df['CELULAR'].astype('str')
df['CELULAR'] = '57'+df['CELULAR'] 

#Find the insurance with the cheapest value 
df['menor_valor'] = df.min(1)
#Set format to the value 
df.loc[:, "Menor valor formato"] ='$'+ df["menor_valor"].map('{:,.2f}'.format)
#Divide the minimun value into 10 to find the value financed to 10 months
df['cuotas_format'] = ((df.min(1)*1.10)/10)
#Set format to the value
df.loc[:, "Cuotas"] ='$'+ df["cuotas_format"].map('{:,.2f}'.format)
#Find the name of the insurance carrier (is the name of the column of minimun vaulue)
df['nombre_aseguradora'] = df.loc[df.index].eq(df.menor_valor, axis=0).idxmax(axis=1)
#Drop inecessary columns
df = df.drop(columns =  ['MAPFRE', 'AXA', 'ALLIANZ', 'ESTADO', 'HDI', 'LIBERTY', 'EQUIDAD', 'ZURICHC', 'SBS',  'BOLIVAR', 'menor_valor', 'VALOR ASEGURADO', 'cuotas_format',])

#Interate over the pandas dataframe to send the personalized message with whatsapp api
for index, row in df.iterrows():
  #The value row is a pandas series of the row

    #Convert the pandas series intno a list to iterete over values 
    listValues = row.tolist()

    name = listValues[0]
    numberTel = listValues[1]
    totalValue = listValues[2]
    financed = listValues[3]
    insurance =  listValues[4]
    #Send the message to the client with whatsapp api

    #This if is to not sent repeated messages
    if numberTel not in numbersSents:
      whatsappSender(numeroCliente= numberTel, nombreCliente=name, aseguradora=insurance, valorTotal=totalValue, CuotasValor=financed)
      numbersSents.append(numberTel)
      numberSaver(numberTel)
      print('Succesfully sent the message')
      print('--------------------')
    
    else:
      print('The message has alredy been sent')
      pass 

opener.close()

df.to_excel('final.xlsx', index= False)


