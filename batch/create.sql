use studspot_db;

drop table if exists review;
drop table if exists spot;
drop table if exists user;
 
create table user (
    uid int not null auto_increment,
    w_email varchar(25) not null,
    username varchar(50) not null,
    hashed char(60),
    unique(username),
    index(uid),
    primary key (uid)
)
ENGINE = InnoDB;
 
create table spot (
   sid int not null auto_increment,
   author int,
   spotname varchar(50),
   description varchar(500),
   location enum('Boston', 'Cambridge', 'Wellesley On-Campus', 'Wellesley Off-Campus'),
   amenities set('Bathrooms', 'Drinks', 'Food', 'Outlets', 'Wifi'),
   status enum('Open', 'Temporarily Closed', 'Permanently Closed'),
   photo varchar(100),
   primary key (sid),
   index(sid),
   foreign key (author) references user(uid)
       on delete restrict
       on update restrict
)
ENGINE = InnoDB;
 
create table review (
   rid int not null auto_increment,
   sid int not null,
   rating enum('0','1','2','3','4','5'),
   comment varchar(500),
   author int,
   primary key (rid),
   index (rid),
   foreign key (author) references user(uid)
       on delete restrict
       on update restrict,
   foreign key (sid) references spot(sid)
       on delete restrict
       on update restrict
)
ENGINE = InnoDB;
