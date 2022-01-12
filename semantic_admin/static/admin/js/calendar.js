/*global gettext, interpolate, ngettext*/
'use strict';

const days = [
    'Sunday', 
    'Monday', 
    'Tuesday', 
    'Wednesday', 
    'Thursday', 
    'Friday', 
    'Saturday', 
];

const months = [
    'January', 
    'February', 
    'March', 
    'April', 
    'May', 
    'June', 
    'July', 
    'August',
    'September',
    'October',
    'November',
    'December'
];

const calendarI18n = {
    days: ['S', 'M', 'T', 'W', 'T', 'F', 'S'].map(function(oneLetterDay, index) { 
        const day = days[index];
        return pgettext(`one letter ${day}`, oneLetterDay) 
    }),
    months: months.map(function(month) { 
        return gettext(month) 
    }),
    monthsShort: [
        'Jan', 
        'Feb', 
        'Mar', 
        'Apr', 
        'May', 
        'Jun', 
        'Jul', 
        'Aug', 
        'Sep', 
        'Oct', 
        'Nov', 
        'Dec'
    ].map(function(monthShort, index) { 
        const monthLong = months[index];
        return pgettext(`abbrev. month ${monthLong}`, monthShort) 
    }),
    today: gettext('Today'),
    now: gettext('Now')
}

function dateFormatter(date, settings) {
  if (!date) return '';
  return new Intl.DateTimeFormat({ dateStyle: 'short', timeStyle: 'short' }).format(date);
}

const calendarFormatter = {
  date: dateFormatter,
}
