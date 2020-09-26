import json

def create_file_normal(filename, value):
  with open (filename, 'a') as f:
      f.write(value)
      f.write('\n')

def create_file_json1(filename, value, time='0'):
    with open (filename, 'a') as f:
        f.write(time)
        f.write('\n')
        json.dump(value,f)
        f.write('\n')

def create_file_json(filename, value):
    with open (filename, 'a') as f:
        json.dump(value,f)
        f.write('\n')


def read_file_json(filename):
    with open(filename, 'r') as f:
        lineList = f.readlines()
    return lineList

'''
lineList = read_file_json('rwText_json.txt')
print len(lineList)
#print data
#print data['1']['HouseMeterRealPower']
#print data['2']['soc']
'''
'''
house_dict = {1: {'Timestep':'2017-07-01 00:00:00 EDT', 'HouseMeterRealPower': 6165.12, 'soc': 0.437827, 'BatteryReactivePower': 3.46945e-18, 'BatteryRealPower': 1000.0,'HouseMeterReactivePower': 92.5561, 'SolarReactivePower': 0.0, 'SolarRealPower': 0.0}, 2: {'Timestep':'2017-07-01 00:00:00 EDT','HouseMeterRealPower': 0.0, 'HouseMeterReactivePower': 0.0}, 3: {'Timestep':'2017-07-01 00:00:00 EDT','HouseMeterRealPower': 0.0, 'soc': 0.5, 'BatteryReactivePower': 0.0, 'BatteryRealPower': 0.0, 'HouseMeterReactivePower': 0.0, 'SolarReactivePower': 0.0, 'SolarRealPower': 0.0}}
house_dict_2 = {1: {'Timestep':'2017-07-01 08:00:00 EDT','HouseMeterRealPower': 6969.12, 'soc': 0.437827, 'BatteryReactivePower': 3.46945e-18, 'BatteryRealPower': 1000.0,'HouseMeterReactivePower': 92.5561, 'SolarReactivePower': 0.0, 'SolarRealPower': 0.0}, 2: {'Timestep':'2017-07-01 01:00:00 EDT','HouseMeterRealPower': 0.0, 'HouseMeterReactivePower': 0.0}, 3: {'Timestep':'2017-07-01 01:00:00 EDT','HouseMeterRealPower': 0.0, 'soc': 0.5, 'BatteryReactivePower': 0.0, 'BatteryRealPower': 0.0, 'HouseMeterReactivePower': 0.0, 'SolarReactivePower': 0.0, 'SolarRealPower': 0.0}}

#create_file_normal('rwText_normal.txt',house_dict)
create_file_json('rwText_json.json',house_dict)
create_file_json('rwText_json.json',house_dict_2)

# reading file
lineList = read_file_json('rwText_json.json')
print len(lineList)
#print lineList[1]
data = json.loads(lineList[-1])
print data
print data['1']['Timestep']
print data['1']['HouseMeterRealPower']
'''
