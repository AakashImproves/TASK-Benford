from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.view import view_config
import os
import csv
import shutil
import math

@view_config(
    route_name='benford',
    renderer='templates/inputfile.jinja2',
    request_method='GET'
)
def home(request):
    return {}

@view_config(
    route_name='benford',
    renderer='json',
    request_method='POST'
)
def benford(request):
    uploaded_file = request.POST['file']
    input_file = uploaded_file.file
    filename  = uploaded_file.filename
    # get current directory 
    file_path = os.path.join('/', os.path.abspath(os.path.dirname(__file__)) + '/tmp', filename)
    input_file.seek(0)
    # save uploaded file to current directory
    with open(file_path, 'wb') as output_file:
      shutil.copyfileobj(input_file, output_file)
    
    return read_file(file_path)

def read_file(file_path):
  first_digits = []

  with open(file_path) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
      first_digit = get_first_digit(row[0])
      first_digits.append(first_digit)
  os.remove(file_path)
  
  len_of_list = len(first_digits) 
  chi_square = 0
  json_list = {}
  
  for f_digit in set(first_digits):
    count_of_f_digit = first_digits.count(f_digit)
    try:
      log_val = math.log10(1+(1/f_digit))*100
      percentage = round((count_of_f_digit/len_of_list) * 100, 2)
      chi_square += (percentage - log_val)**2 / log_val
      chi_square *= 100
      json_list[f_digit] = "Number of {digit} is {count} and the percentage is {percentage}%." . format(digit = f_digit, count = count_of_f_digit, percentage = percentage)
    except:
      print("Some error while calcualtion of digit {val}" . format(val = f_digit))
  
  is_justified = "Benford is justified" if (chi_square < 15.51) else "Benford is not justified"
  
  return {"msg": is_justified, "json_data": json_list}

def get_first_digit(digit):
  if(digit.isdigit()):
    if(int(digit) >= 10):
      digit = str(digit)[0]
    
    return int(digit)
    
if __name__ == '__main__':
    with Configurator() as config:
        config.add_route('benford', '/')
        config.include('pyramid_jinja2')
        config.scan()
        app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 6543, app)
    server.serve_forever()