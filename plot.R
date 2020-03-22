library(blogdown)
library(tidyr)
library(dplyr)
library(DiagrammeR)
library(plotly)

sleepdf=read.csv('data/sleep.csv',header=TRUE)
heartdf=read.csv('data/heart.csv',header=TRUE)
eventdf=read.csv('data/calendar.csv',header=TRUE)
locdf=read.csv('data/location.csv',header=TRUE)
loctype=read.csv('data/location_types.csv',header=TRUE,fileEncoding="UTF-8-BOM")

sleepdf$start=as.POSIXct(sleepdf$start, format = "%Y-%m-%dT%H:%M:%S")
sleepdf$end=as.POSIXct(sleepdf$end, format = "%Y-%m-%dT%H:%M:%S")
eventdf$start=as.POSIXct(eventdf$start, format = "%Y-%m-%dT%H:%M:%S")
eventdf$end=as.POSIXct(eventdf$end, format = "%Y-%m-%dT%H:%M:%S")
locdf$start=as.POSIXct(locdf$start/1000, origin="1970-01-01", tz='EST')
locdf$end=as.POSIXct(locdf$end/1000, origin="1970-01-01", tz='EST')


locdf$location2 <- loctype$location[match(locdf$location, loctype$value)]
locdf$event <- loctype$event[match(locdf$location, loctype$value)]


workout_start =numeric(10)
workout_end = numeric(10)
heartdf$Heart.Rate=as.numeric(heartdf$Heart.Rate)
active=FALSE
count=0
workout_n=1

for(i in 1:(nrow(heartdf))){
  if(heartdf$Heart.Rate[i]>100){
    count=5
    if(active==FALSE){
      workout_start[workout_n]=i
      active=TRUE
    }
  }
  else{
    count=count-1
    if(active==TRUE){
      if(count<1){
        workout_end[workout_n]=i
        workout_n=workout_n+1
        active=FALSE
      }
    }
  }
}
activitydf<-data.frame(as.POSIXct(paste(heartdf$Date[workout_start],heartdf$Time[workout_start]), format="%Y-%m-%d %H:%M:%S"),
                       as.POSIXct(paste(heartdf$Date[workout_end],heartdf$Time[workout_end]), format="%Y-%m-%d %H:%M:%S"),
                       "workout")

names(activitydf)=c("start","end","group")

activitydf$event="exercise"
sleepdf$event="sleep"

fig <- plot_ly()
tograph<-function(fig,data,colour,level){
  for(i in 1:(nrow(data) )){
    fig = add_trace(fig,
      x = c(data$start[i], data$end[i]),  
      y = c(level, level),
      type="scatter",
      mode = "lines",
      line = list(color = colour, width = 100),
      showlegend = F, 
      text = paste("Event: ", data$event[i], "<br>") )
  }
  return(fig)
}

drivingdf=locdf[locdf$event=="driving",]
otherdf=locdf[!locdf$event=="driving"&!locdf$location2=="home",]
fig=tograph(fig,sleepdf,"blue",0)
fig=tograph(fig,activitydf,"orange",1)
fig=tograph(fig,eventdf,"red",4)
fig=tograph(fig,drivingdf,"purple",2)
fig=tograph(fig,otherdf,"green",3)

fig=fig %>% layout(title="Schedule March 20, 2020",margin=list(t=50),xaxis=list(range=c("2020-03-20","2020-03-21"),type="date"), 
                    yaxis = list(showgrid = F,tickmode = "array", tickvals = c(0,1,2,3,4), 
                                 ticktext = c("Sleep","exercise","drive","other","event"),tickfont=list(size=15)))

fig

