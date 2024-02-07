import React from 'react';
import ReactDOM from 'react-dom/client';
import OpenButton from './components/OpenButton.jsx';
import DisplaySettingPopper from './components/DisplaySettingPopper.jsx';
import DisplayCommandPopper from './components/DisplayCommandPopper.jsx';
import PlayerSlider from './components/Player.jsx';
import DisplayTablePopper from './components/DisplayTablePopper.jsx';
import DisplayTreePopper from './components/DisplayTreePopper.jsx';


function generateGetBoundingClientRect(x = 0, y = 0) {
  return () => ({
    width: 0,
    height: 0,
    top: y,
    right: x,
    bottom: y,
    left: x
  });
}

function createVirtualElement(x=0, y=0, xrel=0, yrel=0) {
  return {
    xrel: xrel,
    yrel: yrel,
    x: x,
    y: y,
    getBoundingClientRect: generateGetBoundingClientRect(x, y),
    moveTopRight: function(w){
      this.x = w + this.xrel
      this.getBoundingClientRect = generateGetBoundingClientRect(this.x, this.y)
    },
    moveBottomLeft: function(h){
      this.y = h + this.yrel
      this.getBoundingClientRect = generateGetBoundingClientRect(this.x, this.y)
    },
    moveBottomRight: function(w, h){
      this.x = w + this.xrel
      this.y = h + this.yrel
      this.getBoundingClientRect = generateGetBoundingClientRect(this.x, this.y)
    },
    moveBottom: function(w, h){
      this.x = Math.round(w / 2) + this.xrel
      this.y = h + this.yrel
      this.getBoundingClientRect = generateGetBoundingClientRect(this.x, this.y)
    },
  }
};

const virtualElDenseTable = createVirtualElement(0, 0, -290, -70)
const virtualElButton = createVirtualElement(0, 0, -40, -15)
const virtualElOpenButton = createVirtualElement(40, 15)
const virtualElDisplaySettingPopper = createVirtualElement(110, 0, 20, -70)
const virtualElDisplaySettingButton = createVirtualElement(40, 0, 0, -15)
const virtualElDisplayCommandPopper = createVirtualElement(0, 0, -150, -70)
const virtualElDisplayCommandButton = createVirtualElement(90, 0, 0, -15)
const virtualElPlayer = createVirtualElement(0, 0, 30, -20)
const virtualElDisplayTablePopper = createVirtualElement(0, 0, -335, -70)
const virtualElDisplayTableButton = createVirtualElement(0, 0, -40, -15)
const virtualElDisplayInteractionPopper = createVirtualElement(0, 15, -225, 0)
const virtualElDisplayInteractionButton = createVirtualElement(0, 15, -40, 0)
const virtualElDisplaySelectionPopper = createVirtualElement(0, 15, -225, 0)
const virtualElDisplaySelectionButton = createVirtualElement(0, 65, -40, 0)

var w = window.innerWidth;
var h = window.innerHeight;

virtualElDenseTable.moveBottomRight(w, h)
virtualElButton.moveBottomRight(w, h)
virtualElDisplaySettingPopper.moveBottomLeft(h)
virtualElDisplaySettingButton.moveBottomLeft(h)
virtualElDisplayCommandPopper.moveBottom(w, h)
virtualElDisplayCommandButton.moveBottomLeft(h)
virtualElPlayer.moveBottom(w, h)
virtualElDisplayTablePopper.moveBottomRight(w, h)
virtualElDisplayTableButton.moveBottomRight(w, h)
virtualElDisplayInteractionPopper.moveTopRight(w)
virtualElDisplayInteractionButton.moveTopRight(w)
virtualElDisplaySelectionPopper.moveTopRight(w)
virtualElDisplaySelectionButton.moveTopRight(w)

window.addEventListener( "resize", function( event ){
    w = window.innerWidth;
    h = window.innerHeight;
    virtualElDenseTable.moveBottomRight(w, h);
    virtualElButton.moveBottomRight(w, h);
    virtualElDisplaySettingPopper.moveBottomLeft(h)
    virtualElDisplaySettingButton.moveBottomLeft(h)
    virtualElDisplayCommandPopper.moveBottom(w, h)
    virtualElDisplayCommandButton.moveBottomLeft(h)
    virtualElPlayer.moveBottom(w, h)
    virtualElDisplayTablePopper.moveBottomRight(w, h)
    virtualElDisplayTableButton.moveBottomRight(w, h)
    virtualElDisplayInteractionPopper.moveTopRight(w)
    virtualElDisplayInteractionButton.moveTopRight(w)
    virtualElDisplaySelectionPopper.moveTopRight(w)
    virtualElDisplaySelectionButton.moveTopRight(w)
  }, false );


function createData(name, calories, fat, carbs, protein) {
  return { name, calories, fat, carbs, protein };
}

const rows = [
  createData('Frozen yoghurt', 159, 6.0, 24, 4.0),
  createData('Ice cream sandwich', 237, 9.0, 37, 4.3),
  createData('Eclair', 262, 16.0, 24, 6.0),
  createData('Cupcake', 305, 3.7, 67, 4.3),
  createData('Gingerbread', 356, 16.0, 49, 3.9),
];

const tableData = []
const playerMinMax = [1, 1]
const treePair = []
const treeSelection = []

window.tableData = tableData
window.openbutton = virtualElOpenButton
window.playerMinMax = playerMinMax
window.treePair = treePair
window.treeSelection = treeSelection

const socket = new WebSocket('ws://localhost:12345');

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <div>
      <OpenButton virtualElButton={virtualElOpenButton} socket={socket}/>
      <DisplaySettingPopper virtualElButton={virtualElDisplaySettingButton} virtualElPopper={virtualElDisplaySettingPopper} />
      <DisplayCommandPopper virtualElButton={virtualElDisplayCommandButton} virtualElPopper={virtualElDisplayCommandPopper} />
      <PlayerSlider virtualElPlayer={virtualElPlayer} playerMinMax={playerMinMax} socket={socket} />
      <DisplayTablePopper tableData={tableData} virtualElButton={virtualElDisplayTableButton} virtualElTable={virtualElDisplayTablePopper}/>
      <DisplayTreePopper 
        virtualElDisplayInteractionPopper={virtualElDisplayInteractionPopper}
        virtualElDisplayInteractionButton={virtualElDisplayInteractionButton}
        virtualElDisplaySelectionPopper={virtualElDisplaySelectionPopper}
        virtualElDisplaySelectionButton={virtualElDisplaySelectionButton}
        treePair={treePair}
        treeSelection={treeSelection}
        socket={socket}
      />
    </div>
);
