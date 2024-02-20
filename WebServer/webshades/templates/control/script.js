/* 
Unintuitive required gestures:
* None
Secret shortcuts:
* Right click individual window to reset
*/

// Styles
let skyblue = '#8BC4ED'
let lightgray = '#D9D9D9'

// States
let shiftKey = false

// Load new data from server
let main = 'a50'
let overrides = 'm100,,m-2,'.split(',')
let schedule = 'm55,m0,m-2,a50,a50'.split(',')
let eventName = 'Social Engineering'
function refresh(options={}) {
  // Window autopopulate
  let windowContainer = document.getElementById('windows')
  windowContainer.innerHTML = ""
  let windows = overrides.join(',').split(',')
  console.log(windows)
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
  // Schedule
}

// Rendering
function renderWindowColor(element, value, overriden, manual=false) {
  element.style.setProperty('--background', mixColors(skyblue, lightgray, value/100))
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
refresh()

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
  return '#' + Math.round(rgb[0]).toString(16) + Math.round(rgb[1]).toString(16) + Math.round(rgb[2]).toString(16)
}
function mixColors(hex1, hex2, percent) {
  let color1 = hexToRgb(hex1)
  let color2 = hexToRgb(hex2)
  return rgbToHex([color1[0] * percent + color2[0] * (1 - percent),
  color1[1] * percent + color2[1] * (1 - percent),
  color1[2] * percent + color2[2] * (1 - percent)])
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