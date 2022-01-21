$(document).ready(function () {
    let Calendar = tui.Calendar;
    var $calEl = $('#calendar').tuiCalendar({
      defaultView: 'month',
      taskView: true,
      template: {
        monthDayname: function(dayname) {
          return '<span class="calendar-week-dayname-name">' + dayname.label + '</span>';
        }
      },
        calendars: [
    {
      id: '1',
      name: 'My Calendar',
      color: '#ffffff',
      bgColor: '#9e5fff',
      dragBgColor: '#9e5fff',
      borderColor: '#9e5fff'
    },
    {
      id: '2',
      name: 'Company',
      color: '#00a9ff',
      bgColor: '#00a9ff',
      dragBgColor: '#00a9ff',
      borderColor: '#00a9ff'
    },
    ]
    });
    var calendarInstance = $calEl.data('tuiCalendar');


    calendarInstance.createSchedules([]);
})