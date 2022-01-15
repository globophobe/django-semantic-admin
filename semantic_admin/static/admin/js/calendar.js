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

function getCalendarText(hasJavascriptCatalog) {
  if (hasJavascriptCatalog) {
    return {
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
  }
}

function getCalendarOptions(type, languageCode, calendarOptions, text) {
  const dateStyle = 'short';
  const timeStyle = 'short';

  let defaultFormatterOptions;
  if (type === 'datetime') {
    defaultFormatterOptions = { dateStyle, timeStyle };
  } else if (type === 'date') {
    defaultFormatterOptions = { dateStyle };
  } else if (type === 'time') {
    defaultFormatterOptions = { timeStyle };
  }

  const options = calendarOptions[type];

  let formatterOptions;
  if (options && options.intlDateTimeFormatOptions) {
    formatterOptions = Object.assign({}, options.intlDateTimeFormatOptions)
  } else {
    formatterOptions = defaultFormatterOptions;
  }

  const intlFormatter = new Intl.DateTimeFormat(languageCode, formatterOptions);

  function calendarFormatter(date) {
    if (!date) return '';
    return intlFormatter.format(date)
  }

  let formatter;
  if (type == 'datetime') { 
    formatter = { 
      datetime: function(date, settings, forCalendar) {  
        return calendarFormatter(date)
      }
    }
  } else if (type == 'date') {
    formatter = { 
      date: function(date, settings) {  
        return calendarFormatter(date)
      }
    }
  } else if (type == 'time') {
    formatter = { 
      time: function(date, settings, forCalendar) {  
        return calendarFormatter(date)
      }
    }
  }

  if (options) {
    return Object.assign(options, { type, formatter, text })
  }
  return { type, formatter, text }
}

