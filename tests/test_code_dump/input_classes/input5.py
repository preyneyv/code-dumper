from datetime import date as dt
class Employee:
   def __init__(self, name, age):
      self.name = name
      self.age = age
   @staticmethod
   def isAdult(age):
      if age > 18:
         return True
      else:
         return False
   @classmethod
   def emp_from_year(emp_class, name, year):
       return emp_class(name, dt.today().year - year)

e1 = Employee('Dhiman', 25)
e2 = Employee.emp_from_year('Subhas', 1987)
print(Employee.isAdult(25))
print(Employee.isAdult(16))
