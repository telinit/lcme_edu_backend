from django.db.models import Min, Max
from edu_lnmo.mark.models import *
import datetime

fins = dict(zip(Activity.FinalType.values, Activity.FinalType.labels))


def insert_at(act):
	tail = Activity.objects.filter(course=act.course,order__gte=act.order)
	
	for a in tail:
		a.order += 1
		a.save()
	
	act.save()


def add_fin_activities(fin_date, fin_type):
	cs = Course.objects.filter(~Q(activities__final_type=fin_type)).distinct()
	for c in cs:
		try:
			order = Activity.objects.filter(~Q(date=None), Q(date__gt=fin_date), course=c).aggregate(Min('order'))['order__min']
			if not order:
				raise Exception()
		except:
			try:
				order = Activity.objects.filter(course=c).aggregate(Max('order'))['order__max'] + 1
			except:
				pass
		
		if not order:
			order = 1
		
		insert_at(
			Activity(
				course=c,
				title=fins[fin_type],
				order=order, 
				content_type=Activity.ActivityContentType.FIN,
				final_type=fin_type,
				date=fin_date,
			)
		)
		
add_fin_activities(datetime.datetime(2022,10,27), Activity.FinalType.Q1)
add_fin_activities(datetime.datetime(2022,12,30), Activity.FinalType.Q2)
add_fin_activities(datetime.datetime(2022,12,30), Activity.FinalType.H1)
add_fin_activities(datetime.datetime(2023,3,23), Activity.FinalType.Q3)
add_fin_activities(datetime.datetime(2023,5,31), Activity.FinalType.Q4)
add_fin_activities(datetime.datetime(2023,5,31), Activity.FinalType.H2)
add_fin_activities(datetime.datetime(2023,5,31), Activity.FinalType.Y)
