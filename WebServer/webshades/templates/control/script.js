dragBars = document.getElementsByClassName('window-bar')
for (let i = 0; i < dragBars.length; i++) {
  element = dragBars[i]
  element.addEventListener('mousedown', console.log)
  console.log(element)
}