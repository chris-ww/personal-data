library(blogdown)
library(tidy)
library(dplyr)
library(DiagrammeR)
library(shiny)
library(ProjectTemplate)
library(DBI)
library(RSQLite)
library(d3Dashboard)
library("shinyWidgets")
source("bullet_graph.R")
#code for bullet graph https://github.com/mtorchiano/MTkR, mine is slightly modified
library(ggplot2)

##################Connecting to History Database#######################
conn <- dbConnect(RSQLite::SQLite(), "personal_data.db")
  activitydf=dbReadTable(conn, "activity")
  sleepdf=dbReadTable(conn, "sleep")
  fooddf=dbReadTable(conn, "food")
  bodydf=dbReadTable(conn, "body")
  rescuedf=dbReadTable(conn, "rescue")
dbDisconnect(conn)

#standardising dates
sleepdf$start=as.POSIXct(sleepdf$start, format = "%Y-%m-%dT%H:%M:%S")
sleepdf$end=as.POSIXct(sleepdf$end, format = "%Y-%m-%dT%H:%M:%S")


##################Connecting to daily Databases#######################
update_fitbit=function(){
  system2("wsl", "python3 trigger_import.py")
  conn <- dbConnect(RSQLite::SQLite(), "personal_data_trigger.db")
    activitydf2=dbReadTable(conn, "activty")
    sleepdf2=dbReadTable(conn, "sleep")
    fooddf2=dbReadTable(conn, "meals")
    rescuedf2=dbReadTable(conn, "rescue")
  dbDisconnect(conn)
  daily=list(sleepdf2,activitydf2,fooddf2,rescuedf2)
  daily
}

daily=update_fitbit()
sleep_day=daily[[1]]
activity_day=daily[[2]]
food_day=daily[[3]]
rescue_day=daily[[4]]

#standardising dates
sleep_day$start=as.POSIXct(daily[[1]]$start, format = "%Y-%m-%dT%H:%M:%S")
sleep_day$end=as.POSIXct(daily[[1]]$end, format = "%Y-%m-%dT%H:%M:%S")

#If no meals set calories etc to 0 instead of NA
food_day[1,][is.na(daily[[3]][1,])]=0




###########Plotting ##############################################

check_metrics=function(sleep_day,food_day,activity_day,rescue_day){
  #Creating variables for readability
  unproductive=sum(rescue_day[rescue_day[,6]<0,2])/60
  productive=sum(rescue_day[rescue_day[,6]>0,2])/60
  activity=(sum(activity_day[,c(6,7)])+activity_day[[2]][,8]/5)/60
  avg_cal=mean(tail(activitydf$Calories.Out,5))
  cal_in=food_day[1,3]
  protein=food_day[1,4]
  sleep=sleep_day[1,5]/60
  restless=sleep_day[1,9]/60
  daily_score=productive-unproductive+activity+protein/100+sleep/10-restless
  
  today=as.POSIXct(format(Sys.Date(),format="%Y-%m-%d"),format="%Y-%m-%d")
  hour=as.numeric(difftime(Sys.time(),today,units="hours"))
  
  #percent of Day/Awake day passed
  pd=min(((hour-9)/14),1)
  pw=min(((hour-9)/8),1)
  
  #bullet graphs
  par(mfrow=c(8,1),mar=c(1,8,1,1),oma = c(1, 0, 2, 0))
  bulletgraph(x=daily_score,limits=c(0,6,8,max(10,daily_score)),ref=8*pw, name="score")
  bulletgraph(x=sleep,limits=c(min(6,sleep),7,7.75,max(9,sleep)),ref=7.75, name="sleep",subname="hours")
  bulletgraph(x=restless,limits=c(0,.333,.75,max(1.33,restless)),ref=.333, name="restless",rev=T,subname="hours")
  bulletgraph(x=cal_in,limits=c(min(0,cal_in-1),avg_cal-300,avg_cal-150,avg_cal+150,avg_cal+300,max(avg_cal+500,cal_in+100)),ref=avg_cal*pd, name="Calories",rev=T)
  bulletgraph(x=protein,limits=c(min(0,protein),140,170,max(200,protein)),ref=170*pd, name="protein",subname="grams")
  bulletgraph(x=activity,limits=c(min(0,activity),1,1.5,max(2,activity)),ref=1.5*pw, name="activity", subname="hours")
  bulletgraph(x=productive,limits=c(0,2,3,4,max(5,productive)),ref=4*pw, name="productive",subname="hours")
  bulletgraph(x=unproductive,limits=c(0,0.5,1,max(1.5,unproductive)),ref=0.5*pw, name="unproductive",subname="hours")
}

#Categorising rescuetime productivity data 1,2 =productive,-1,-2 =unproductive
rescue_histdf=rescuedf
rescue_histdf$productive[rescue_histdf$productive>0]="productive"
rescue_histdf$productive[rescue_histdf$productive<0]="unproductive"
rescue_histdf=rescue_histdf[!rescue_histdf$productive==0,]

#Getting sums of productive and unproductive activities per day
rescue_histdf<-rescue_histdf %>%
  group_by(date,productive) %>%
  summarise(duration=sum(duration))

#Plotting rescuetime, sleep, activity and weight history
ggplot(rescue_histdf)+
  geom_line(aes(x=as.Date(date),y=duration/60,lty=productive))+
  xlab("date")+
  ylab("duration(minutes)")+
  ylim(0,NA)

ggplot(sleepdf)+
  geom_line(aes(x=as.Date(date),y=minutes.asleep/60,lty="Sleep"))+
  geom_line(aes(x=as.Date(date),y=restless.duration/60,lty="restless.duration"))+
  xlab("date")+
  ylab("duration (hours)")+
  ylim(0,NA)


ggplot(activitydf)+
  geom_line(aes(x=as.Date(Date),y=very.active.minutes,lty="Very active"))+
  geom_line(aes(x=as.Date(Date),y=fairly.active.minutes,lty="Fairly active"))+
  geom_line(aes(x=as.Date(Date),y=lightly.active.minutes,lty="Lightly active"))+
  xlab("date")+
  ylab("duration (minutes)")+
  ylim(0,NA)

bodydf=bodydf[bodydf$weight>0,]
ggplot(bodydf)+
  geom_line(aes(x=as.Date(date),y=weight))+
  xlab("date")+
  ylab("weight (lbs)")+
  ylim(0,190)


