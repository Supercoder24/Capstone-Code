// Load new data from server
function refresh() {
  // Window autopopulate
  document.getElementById('windows').innerHTML = ""
  for (let i = 0; i < windows; i++) {
    // Add window elements to page with given values and states
  }
  // Main controls
  // Schedule
}

// Window functionality
dragBars = document.getElementsByClassName('window-bar')
for (let i = 0; i < dragBars.length; i++) {
  element = dragBars[i]
  element.addEventListener('mousedown', (event) => {
    console.log('Clicked', event)
    if (event.target.innerText == "Click to Open") {
      console.log('Opening...')
      event.target.parentNode.classList.remove('closed')
      event.target.parentNode.classList.add('open')
      event.target.innerText = "Click to Close"
    } else {
      console.log('Closing...')
      event.target.parentNode.classList.remove('open')
      event.target.parentNode.classList.add('closed')
      event.target.innerText = "Click to Open"
    }
  })
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