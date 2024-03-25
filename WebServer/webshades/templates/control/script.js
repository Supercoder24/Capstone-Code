/* 
Unintuitive required gestures:
* None
Secret shortcuts:
* Right click individual window to reset
*/

// Styles
let light = {
  'skyblue': '#8BC4ED',
  'lightgray': "#D9D9D9",
}

let dark = {
  'skyblue': '#0095d2',
  'lightgray': '#323232'
}

let theme = light

let skyblue = '#0095d2'
let lightgray = '#323232'

// States
let shiftKey = false
let timeout = -1
let lastMain = 'a50'

// Load new data from server
let main = 'a50'
let overrides = 'm100,,m-2,'.split(',')
let schedule = 'm55,m0,m-2,a50,a50'.split(',')
let eventName = 'Social Engineering'

function showError(response) { // console.log(response); return response.json()}).then((response) => {
  console.log(response)
  let eElement = document.getElementById('errors')
  console.log(eElement)
  eElement.innerHTML = ''
  if (typeof response == 'string') {
    console.log('String')
    let errorE = document.createElement('div')
    errorE.classList.add('flash')
    errorE.innerText = response
    console.log(errorE)
    eElement.appendChild(errorE)
    console.log(eElement.innerHTML)
  } else {
    if (response.errors && response.errors.length > 0) {
      for (let i = 0;i < response.errors.length; i++) {
        let errorE = document.createElement('div')
        errorE.classList.add('flash')
        errorE.innerText = response.errors[i]
        eElement.appendChild(errorE)
      }
    }
    if (response.success) {
      let errorE = document.createElement('div')
      errorE.classList.add('flash')
      errorE.classList.add('success')
      errorE.innerText = response.success
      eElement.appendChild(errorE)
    }
  }
  console.log(eElement.innerHTML)
}

// # schedule = {
//   #     "name": "Ha", # Name of the current event - from Cole
//   #     "variables": 'm100', # Variables for the current event - from Cole
//   #     'now': 'Tuesday Feb 27, 2024', # Date formatting
//   #     'events': [
//   #         '9:15 Social Engineering', # [id, stringOfName, stringOfTime, stringOfDaysofWeek] # binary for days of week (mon, tues, wed...)
//   #         '10:20 Social Engineering'
//   #     ]
//   # }
function refresh(options={}) {
  // Window autopopulate
  let windowContainer = document.getElementById('windows')
  windowContainer.innerHTML = ""
  let windows = overrides.join(',').split(',')
  console.log(windows)
  if (main == 's') {
    let valid = schedule.length == overrides.length
    for (let i = 0; i < schedule.length; i++) {
      if (schedule[i] == '') {
        valid = false
      }
    }
    if (!valid) {
      main = lastMain
      refresh()
      showError('Invalid schedule')
      return
    }
  }
  for (let i = 0; i < windows.length; i++) {
    let overriden = true
    if (windows[i] == '') {
      if (main[0] == 'm' || main[0] == 'a') {
        windows[i] = main
      } else {
        windows[i] = schedule[i]
      }
      overriden = false
    }
    let mode = windows[i][0]
    let value = parseInt(windows[i].substring(1))
    console.log('Val:',value)
    // Add window elements to page with given values and states
    let window = document.createElement('div')
    window.classList.add('window')
    window.dataset.windowIndex = i
    if (mode == 'm') {
      if (value >= 0) {
        window.classList.add('closed')
        renderWindowColor(window, (100 - value), overriden)
        // window.style.setProperty('--percent', value/100) // Cool striped pattern
      } else if (value == -2) {
        window.classList.add('open')
        overriden ? window.classList.add('override') : null
      } else {
        window.classList.add('stopped')
        overriden ? window.classList.add('override') : null
      }
    } else if (mode == 'a') {
      window.classList.add('closed')
      window.classList.add('auto')
    }
    let inside = document.createElement('div')
    inside.classList.add('window-inside')
    let slider = document.createElement('input')
    slider.classList.add('window-slider')
    slider.type = 'range'
    slider.min = 0
    slider.max = 100
    if (mode == 'm') {
      slider.value = (100 - value)
    } else {
      slider.value = value
    }
    slider.dataset.lastValue = value
    inside.appendChild(slider)
    window.appendChild(inside)
    let outside = document.createElement('div')
    outside.classList.add('window-outside')
    window.appendChild(outside)
    let bar = document.createElement('div')
    bar.classList.add('window-bar')
    if (mode == 'm') {
      if (value >= 0) {
        bar.innerText = 'Click to Open'
      } else if (value == -2) {
        bar.innerText = 'Click to Close'
      } else {
        bar.innerText = 'Stopped'
      }
    } else if (mode == 'a') {
      bar.innerText = 'Click to Open'
    }
    window.appendChild(bar)
    if (shiftKey) {
      let stopButton = document.createElement('button')
      stopButton.classList.add('window-reset')
      stopButton.innerText = 'Stop'
      stopButton.onclick = () => {
        console.log('clicked')
        stop(i)
      }
      window.appendChild(stopButton)
    } else if (overriden) {
      let resetButton = document.createElement('button')
      resetButton.classList.add('window-reset')
      resetButton.innerText = 'Reset'
      resetButton.onclick = () => {reset(i)}
      window.appendChild(resetButton)
    }
    windowContainer.appendChild(window)
  }
  addBarListeners()
  addSliderListeners()
  addWindowListeners()
  console.log(windows)
  // Main controls
  let modeContainer = document.getElementById('mode-selector')
  let modes = modeContainer.children
  for (let i = 0; i < modes.length; i++) {
    if ((modes[i].id == 'sched' && main[0] == 's') ||
     (modes[i].id == 'man' && main[0] == 'm') ||
     (modes[i].id == 'auto' && main[0] == 'a')) {
      modes[i].classList.add('active')
    } else {
      modes[i].classList.remove('active')
    }
  }
  if (main[0] == 'm' || main[0] == 'a') {
    if (parseInt(main.substring(1)) >= 0) {
      document.getElementById('main-value').innerText = main.substring(1) + '%'
    } else if (parseInt(main.substring(1)) == -2) {
      document.getElementById('main-value').innerText = 'Raised'
    } else {
      document.getElementById('main-value').innerText = 'Stopped'
    }
    if (!options.noSetMain) {
      document.getElementById('main-slider').value = parseInt(main.substring(1))
    }
    document.getElementById('main-slider').disabled = false
  } else {
    document.getElementById('main-value').innerText = eventName
    document.getElementById('main-slider').disabled = true
  }
  let masterReset = document.getElementById('reset')
  if (shiftKey) {
    masterReset.innerText = 'Stop'
    masterReset.onclick = () => {stop()}
  } else {
    masterReset.innerText = 'Reset'
    masterReset.onclick = () => {reset()}
  }
  document.getElementById('errors').innerHTML = ''
  // Schedule
  if (timeout != -1) {
    clearTimeout(timeout)
    timeout = setTimeout(send, 3000)
  } else {
    timeout = 0
  }
}

// Rendering
function renderWindowColor(element, value, overriden, manual=false) {
  element.style.setProperty('--background', mixColors(theme.skyblue, theme.lightgray, value/100))
  if (manual) {
    element.classList.remove('auto')
  }
  overriden ? element.classList.add('override') : null
}

// Window functionality
function addBarListeners() {
  let dragBars = document.getElementsByClassName('window-bar')
  for (let i = 0; i < dragBars.length; i++) {
    let element = dragBars[i]
    element.addEventListener('mousedown', (event) => {
      console.log('Clicked', event)
      let windowIndex = parseInt(event.target.parentNode.dataset.windowIndex)
      if (event.target.innerText == "Click to Open") {
        console.log('Opening...')
        overrides[windowIndex] = 'm-2'
        refresh()
        // event.target.parentNode.classList.remove('closed')
        // event.target.parentNode.classList.add('open')
        // event.target.innerText = "Click to Close"
      } else {
        console.log('Closing...')
        overrides[windowIndex] = 'm100'
        refresh()
        // event.target.parentNode.classList.remove('open')
        // event.target.parentNode.classList.add('closed')
        // event.target.innerText = "Click to Open"
      }
    })
  }
}
function addSliderListeners() {
  let sliders = document.getElementsByClassName('window-slider')
  for (let i = 0; i < sliders.length; i++) {
    let element = sliders[i]
    element.addEventListener('mousedown', (event) => {
      event.target.parentNode.classList.add('override')
    })
    element.addEventListener('input', (event) => {
      console.log('Value: ', event.target.value)
      let windowIndex = parseInt(event.target.parentNode.parentNode.dataset.windowIndex)
      overrides[windowIndex] = 'm' + (100 - event.target.value).toString()
      renderWindowColor(event.target.parentNode.parentNode, event.target.value, true, true)
    })
    element.addEventListener('change', (event) => {
      let windowIndex = parseInt(event.target.parentNode.parentNode.dataset.windowIndex)
      overrides[windowIndex] = 'm' + (100 - event.target.value).toString()
      refresh()
    })
  }
}
function addWindowListeners() {
  let windows = document.getElementsByClassName('window')
  for (let i = 0; i < overrides.length; i++) {
    let element = windows[i]
    element.addEventListener('contextmenu', (event) => {
      event.preventDefault()
      console.log('Resetting...', i)
      reset(i)
      refresh()
    })
  }
}
function addScheduleListeners() {
  let items = document.getElementById('schedule').children[1].children
  for (let i = 0; i < items.length; i++) {
    items[i].dataset.eventIndex = i
    items[i].addEventListener('contextmenu', (event) => {
      console.log(event.target.dataset.eventIndex)
      let contextmenu = document.getElementById('contextmenu')
      contextmenu.style.left = event.pageX + 'px'
      contextmenu.style.top = event.pageY + 'px'
      contextmenu.style.display = 'block'
      eventIndex = parseInt(event.target.dataset.eventIndex)
      event.preventDefault()
    })
  }
}

function displaySchedule() {
  let scheduleContainer = document.getElementById('schedule')
  scheduleContainer.innerHTML = ''
  let heading = document.createElement('h1')
  heading.innerText = scheduleIn.now
  scheduleContainer.appendChild(heading)
  let list = document.createElement('ol')
  for (let i = 0; i < scheduleIn.events.length; i++) {
    let event = scheduleIn.events[i]
    let element = document.createElement('li')
    element.innerText = event[2] + ' - ' + event[1]
    element.dataset.eventId = event[0]
    list.appendChild(element)
  }
  scheduleContainer.appendChild(list)
  addScheduleListeners()
}

displaySchedule()

function renameEvent() {
  if (eventIndex != -1) {
    // console.log('Renaming: ', eventIndex)
    let newName = prompt('What is the new name for event ' + scheduleIn.events[eventIndex][1] + '?')
    if (newName) {
      console.log('Renaming ' + eventIndex + ' to ' + newName)
    }
    // Need to request /room/<roomname>/<eventid>/renameevent
    // Need to send new name
  }
}

function editEvent() {
  if (eventIndex != -1) {
    console.log('Editing: ', eventIndex)
    populateEventEditingPopup()
    // Need to request /room/<roomname>/<eventid>/editevent
    // Need to send days: 0111001
    // Need to send tod: military time 700
    // Need to send variables
  }
}

function deleteEvent() {
  if (eventIndex != -1) {
    if (confirm('Are you sure you want to delete event ' + scheduleIn.events[eventIndex][1] + '?')) {
      console.log('Deleting: ', eventIndex)
      // Need to request /room/<roomname>/<eventid>/deleteevent
    }
  }
}

// Reset
function reset(index=-1) {
  if (index == -1) {
    for (let i = 0; i < overrides.length; i++) {
      overrides[i] = ''
    }
  } else {
    overrides[index] = ''
  }
  refresh()
}

// Stop
function stop(index=-1) {
  if (index == -1) {
    main = 'm-1'
  } else {
    overrides[index] = 'm-1'
  }
  refresh()
}

// Change mode
function changeMode(mode) {
  if (mode == 'm' || mode == 'a') {
    let value = document.getElementById('main-slider').value
    if (main[0] != mode[0]) {
      value = 100 - value
    }
    main = mode + value
  } else {
    main = 's'
  }
  refresh()
}

// Change main value
function changeMainValue(event) {
  let value = event.target.value
  if (main[0] == 'm' || main[0] == 'a') {
    main = main[0] + value.toString()
  }
  refresh()
}
document.getElementById('main-slider').addEventListener('change', changeMainValue)
function inputMainValue(event) {
  let value = event.target.value
  if (main[0] == 'm' || main[0] == 'a') {
    main = main[0] + value.toString()
  }
  refresh({'noSetMain':true})
}
document.getElementById('main-slider').addEventListener('input', inputMainValue)

// Master controls
function tiltOpen() {
  main = 'm0'
  refresh()
}
function closeAll() {
  main = 'm100'
  refresh()
}
function raiseAll() {
  main = 'm-2'
  refresh()
}

// Special halt
document.addEventListener('keydown', (event) => {
  if (event.key == 'Shift' || event.key == 's') {
    if (!shiftKey) {
      shiftKey = true
      refresh()
    }
  }
})
document.addEventListener('keyup', (event) => {
  if (event.key == 'Shift' || event.key == 's') {
    if (shiftKey) {
      shiftKey = false
      refresh()
    }
  }
})

// Helpers
function hexToRgb(hex) {
  let returned = []
  for (let i = 1; i < 7; i+=2) {
    returned.push(parseInt(hex.substring(i, i+2), 16))
  }
  return returned
}
function rgbToHex(rgb) {
  return '#' + Math.round(rgb[0]).toString(16).padStart(2,'0') + Math.round(rgb[1]).toString(16).padStart(2,'0') + Math.round(rgb[2]).toString(16).padStart(2,'0')
}
function mixColors(hex1, hex2, percent) {
  let color1 = hexToRgb(hex1)
  let color2 = hexToRgb(hex2)
  console.log('Color1',color1,'Color2',color2)
  let returned = rgbToHex([color1[0] * percent + color2[0] * (1 - percent),
  color1[1] * percent + color2[1] * (1 - percent),
  color1[2] * percent + color2[2] * (1 - percent)])
  console.log('Return', returned)
  return returned
}

function changeTheme() {
  if (theme.skyblue == light.skyblue) {
    // Change to Dark Theme
    document.getElementsByTagName('html')[0].classList.add('dark')
    theme = dark
  } else {
    // Change to Light Theme
    document.getElementsByTagName('html')[0].classList.remove('dark')
    theme = light
  }
  refresh()
}

function send() {
  console.log('Sending: Main: ', main, ', Overrides: ', overrides)
  fetch("", {
    method: "POST",
    body: JSON.stringify({
      'main': main,
      'variables': overrides
    }),
    headers: {
      "Content-type": "application/json; charset=UTF-8"
    }
  }).then(response => response.json()).then((response) => {
    if (response.main) {
      main = response.main
    }
    if (response.variables) {
      overrides = response.variables
    }
    refresh()
    showError(response)
  })
}

// Context menu appear
// document.getElementById('schedule').addEventListener('contextmenu', (event) => {
//   console.log(event)
//   event.preventDefault()
// })

// pageX, pageY

// Context menu disappear
let hideContextMenu = (event) => {
  let contextmenu = document.getElementById('contextmenu')
  let editEventPopup = document.getElementById('editEventPopup')
  if (!contextmenu.contains(event.target) && !editEventPopup.contains(event.target)) {
    contextmenu.style.display = 'none'
    closeEventPopup()
    eventIndex = -1
  }
}
document.addEventListener('click', hideContextMenu)

function populateEventEditingPopup() {
  if (eventIndex != -1) {
    let editingContainer = document.getElementById('editEventPopup')
    editingContainer.style.display = 'none'
    editingContainer.innerHTML = ''

    let heading = document.createElement('h1')
    heading.innerText = 'Editing event ' + scheduleIn.events[eventIndex][1]
    editingContainer.appendChild(heading)

    let currentVariablesCheckbox = document.createElement('input')
    currentVariablesCheckbox.type = 'checkbox'
    currentVariablesCheckbox.id = 'applyNewVariables'
    editingContainer.appendChild(currentVariablesCheckbox)

    let currentVariablesLabel = document.createTextNode(' Use Current Variables (instead of Saved Variables)')
    editingContainer.appendChild(currentVariablesLabel)
    // editingContainer.innerHTML += ' Use Current Variables (instead of Saved Variables)'

    editingContainer.appendChild(document.createElement('br'))

    let timeInput = document.createElement('input')
    console.log(timeInput)
    timeInput.type = 'time'
    timeInput.id = 'newTime'
    let timeValue = Math.round(scheduleIn.events[eventIndex][4] / 100).toString().padStart(2, '0') + ':' + (scheduleIn.events[eventIndex][4] % 100).toString().padStart(2, '0')
    // console.log(timeValue)
    timeInput.value = timeValue
    editingContainer.appendChild(timeInput)

    let eventTimeLabel = document.createTextNode(' Event time')
    editingContainer.appendChild(eventTimeLabel)
    // editingContainer.innerHTML += ' Event time'

    let subHeading = document.createElement('h2')
    subHeading.innerText = 'Repeat on:'
    editingContainer.appendChild(subHeading)

    let daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for (let i = 0; i < 7; i++) {
      let checkbox = document.createElement('input')
      checkbox.type = 'checkbox'
      console.log('Checked? ', scheduleIn.events[eventIndex][3].charAt(i) == 1)
      checkbox.checked = scheduleIn.events[eventIndex][3].charAt(i) == 1
      editingContainer.appendChild(checkbox)

      let dayLabel = document.createTextNode(' ' + daysOfWeek[i] + ' ')
      editingContainer.appendChild(dayLabel)
      // editingContainer.innerHTML += ' ' + daysOfWeek[i] + ' '
    }
    console.log('Val: ', timeInput.value)

    let closeButton = document.createElement('button')
    closeButton.innerText = 'Close'
    closeButton.onclick = closeEventPopup
    editingContainer.appendChild(closeButton)

    let applyButton = document.createElement('button')
    applyButton.innerText = 'Save'
    applyButton.onclick = applyEventEdit
    editingContainer.appendChild(applyButton)

    editingContainer.style.display = 'block'
  }
}

function applyEventEdit() {
  if (eventIndex != -1) {
    console.log('Applying!')
    if (document.getElementById('applyNewVariables').checked) {
      console.log('Updating variables')
    }
    let timeValue = document.getElementById('newTime').value
    let timeInt = timeValue.split(':')[0] * 100 + parseInt(timeValue.split(':')[1])
    console.log(timeInt)
    let dayString = ''
    for (let i = 0; i < 7; i++) {
      dayString += document.getElementById('editEventPopup').getElementsByTagName('input')[i+2].checked ? '1' : '0'
    }
    console.log(dayString)
  } else {
    console.log('No event!')
  }
  closeEventPopup()
}

function closeEventPopup() {
  document.getElementById('editEventPopup').style.display = 'none'
}


// !element.contains(event.target)


function newevent() {
  fetch("/room/I%20have%20no%20clue/newschedule", {
    method: "POST",
    body: JSON.stringify({
      'days': '1111111',
      'variables': 'm23',
        'tod': prompt('What time?'),
        'eventName': prompt('What name?')
    }),
    headers: {
      "Content-type": "application/json; charset=UTF-8"
    }
  }).then(response => console.log)
}

/* Dragging attempt 1
// Add data-mouse-down-at="0" data-old-percent="0" to each element
dragBars = document.getElementsByClassName('window-bar')
for (let i = 0; i < dragBars.length; i++) {
  element = dragBars[i]
  element.addEventListener('mousedown', (event) => {
    console.log(event.type)
    console.log(event.target)
    event.target.dataset.mouseDownAt = event.clientY
    let height = document.getElementsByClassName('window')[0].clientHeight - 25
    console.log(height)
    let sum = 0
    let orig = event.clientY
    let move = (event) => {
      console.log(event.type)
      sum += event.movementY
      percent_offset = (parseFloat(event.target.dataset.mouseDownAt) - event.clientY) / height * 100
      console.log('Offset: ', parseFloat(event.target.dataset.mouseDownAt) - event.clientY)
      console.log('Percent offset: ', percent_offset)
      new_percent = parseFloat(event.target.dataset.oldPercent) + percent_offset
      new_percent = new_percent < 0 ? 0 : new_percent > 100 ? 100 : new_percent
      //event.target.dataset.oldPercent = new_percent
      //event.target.mouseDownAt = event.clientY
      console.log('New percent: ', new_percent)
      new_bottom = new_percent / 100 * (height)
      event.target.style.bottom = 2 * new_bottom + 'px'
      console.log('Height: ', new_percent / 100 * height)
      event.target.parentElement.children[1].style.height = new_percent / 100 * height + 'px'
      // event.target.parentElement.children[0].style.height = height - new_percent / 100 * height + 'px'
      event.target.parentElement.children[1].style.top = - height + (100 - new_percent) / 100 * height + 25 + 'px'
      event.target.parentElement.children[0].children[0].style.opacity = 1 - new_percent / 100
      console.log(event.movementY)
      console.log('Bottom: ', event.target.style.bottom)
      console.log('Sum: ', sum)
      console.log('Abs: ', orig - event.clientY)
    }
    let up = (event) => {
      console.log(event.type)
      event.target.removeEventListener('mousemove', move)
      event.target.removeEventListener('mouseup', up)
    }
    up(event)
    event.target.addEventListener('mousemove', move)
    event.target.addEventListener('mouseup', up)
  })
  // console.log(element)
}
*/