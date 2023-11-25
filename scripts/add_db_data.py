"""
Boostraps the travel_library.db with the project's creators as Users (along with their necessary List objects) along with some sample Places. All instanced objects represent entries into the SQL tables of the Models.py classes.
"""

import json

from run import app
from database import db
from app.models import Blurb, Favoritelist, Place, Searchlist, Travellist, User

with app.app_context():
	# deletes any existing db in URI location before creating
	db.drop_all()
	db.create_all()

	t1 = Travellist(id=1)
	t2 = Travellist(id=2)
	t3 = Travellist(id=3)
	t4 = Travellist(id=4)
	t5 = Travellist(id=5)

	# bootup some Favorite Lists
	f1 = Favoritelist(id=1111)
	f2 = Favoritelist(id=2222)
	f3 = Favoritelist(id=3333)
	f4 = Favoritelist(id=4444)
	f5 = Favoritelist(id=5555)

	# bootup some Search Lists
	s1 = Searchlist(id=11)
	s2 = Searchlist(id=12)
	s3 = Searchlist(id=13)
	s4 = Searchlist(id=14)
	s5 = Searchlist(id=15)

	data1 = {"History": "A place you want to get back to"}
	data2 = {"History": "Wag"}
	data3 = {"History": "Post prohibition"}
	data4 = {"History": "Something to do when its not -25 degrees out"}
	data5 = {"History": "Watch Wall Street and American Psycho"}

	j1 = json.dumps(data1)
	j2 = json.dumps(data2)
	j3 = json.dumps(data3)
	j4 = json.dumps(data4)
	j5 = json.dumps(data5)

	# bootup some test Places
	p1 = Place(
		id=1,
		city="No Place Like Home",
		state="Kansas",
		population=125963,
		activities="Dorothy, lions, tigers, and bears.",
		wiki=j1,
		times_favorited=0,
		times_searched=0,
	)
	p2 = Place(
		id=2,
		city="Dog Town",
		state="Tennessee",
		population=628127,
		activities="probably guitar music and dogs; fishing",
		wiki=j2,
		times_favorited=0,
		times_searched=0,
	)
	p3 = Place(
		id=3,
		city="Bakersfield",
		state="California",
		population=407615,
		activities="go shopping; produce crude oil; drink",
		wiki=j3,
		times_favorited=0,
		times_searched=0,
	)
	p4 = Place(
		id=4,
		city="St. Paul",
		state="Minnesota",
		population=307193,
		activities="fishing; drink coffee",
		wiki=j4,
		times_favorited=0,
		times_searched=0,
	)
	p5 = Place(
		id=5,
		city="New York City",
		state="New York",
		population=98617,
		activities="make money; eating",
		wiki=j5,
		times_favorited=0,
		times_searched=0,
	)

	# create the Users and set their passwords
	u1 = User(
		id=1,
		username="Ethan",
		email="ethan@gmail.com",
		budget=0,
		favoritelist_id=f1.id,
		searchlist_id=s1.id,
		travellist_id=t1.id,
	)
	u2 = User(
		id=2,
		username="Caiden",
		email="caiden@gmail.com",
		budget=0,
		favoritelist_id=f2.id,
		searchlist_id=s2.id,
		travellist_id=t2.id,
	)
	u3 = User(
		id=3,
		username="Jai",
		email="jainder@gmail.com",
		budget=0,
		favoritelist_id=f3.id,
		searchlist_id=s3.id,
		travellist_id=t3.id,
	)
	u4 = User(
		id=4,
		username="Jordan",
		email="jordan@gmail.com",
		budget=0,
		favoritelist_id=f4.id,
		searchlist_id=s4.id,
		travellist_id=t4.id,
	)
	u5 = User(
		id=5,
		username="Tony",
		email="antonio@gmail.com",
		budget=0,
		favoritelist_id=f5.id,
		searchlist_id=s5.id,
		travellist_id=t5.id,
	)

	u1.set_password("e")
	u2.set_password("c")
	u3.set_password("j")
	u4.set_password("j")
	u5.set_password("t")

	# bootup some test Blurbs
	blurb1 = Blurb(
		id=1, content="I love it here in Malibu, bring your whole family!", author_id=1
	)
	blurb2 = Blurb(
		id=2, content="New York City is amazing, I never want to leave.", author_id=2
	)
	blurb3 = Blurb(id=3, content="San Francisco has the best food!", author_id=3)
	blurb4 = Blurb(id=4, content="Austin is so lively and fun!", author_id=4)
	blurb5 = Blurb(id=5, content="Boston has so much history to explore!", author_id=5)

	# add all created objects to the SQL db and commit the changes. (Lists first, then the dependent Users which have foreign keys to those lists)
	db.session.add(t1)
	db.session.add(t2)
	db.session.add(t3)
	db.session.add(t4)
	db.session.add(t5)
	db.session.add(f1)
	db.session.add(f2)
	db.session.add(f3)
	db.session.add(f4)
	db.session.add(f5)
	db.session.add(s1)
	db.session.add(s2)
	db.session.add(s3)
	db.session.add(s4)
	db.session.add(s5)
	db.session.add(p1)
	db.session.add(p2)
	db.session.add(p3)
	db.session.add(p4)
	db.session.add(p5)
	db.session.add(u1)
	db.session.add(u2)
	db.session.add(u3)
	db.session.add(u4)
	db.session.add(u5)
	db.session.add(blurb1)
	db.session.add(blurb2)
	db.session.add(blurb3)
	db.session.add(blurb4)
	db.session.add(blurb5)

	db.session.commit()
