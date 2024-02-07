import {
  Avatar,
  Box,
  Button,
  Checkbox,
  FormControlLabel,
  IconButton,
  Popper,
  styled,
  Typography,
} from '@mui/material';
import React from 'react';
import Icon from '@mui/material/Icon';
import {QWebChannel} from 'qwebchannel';


const Widget = styled('div')(({ theme, width }) => ({
  padding: 3,
  borderRadius: 3,
  border: '2px solid rgba(120, 120, 120, 0.4)',
  width: width,
  maxWidth: '100%',
  margin: 'auto',
  position: 'relative',
  zIndex: 1,
  backgroundColor:
    theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.6)' : 'rgba(100,100,100,0.6)',
  // backdropFilter: 'blur(40px)',
}));

export default function DisplayTreePopper({ 
      virtualElDisplayInteractionPopper,
      virtualElDisplayInteractionButton,
      virtualElDisplaySelectionPopper,
      virtualElDisplaySelectionButton,
      treePair,
      treeSelection,
      socket
  }) {
  const [, forceUpdate] = React.useReducer(x => x + 1, 0);
  const [interactionDisplayed, setInteractionDisplayed] = React.useState(false);
  const [selectionDisplayed, setSelectionDisplayed] = React.useState(false);

  const backendTreePair = function(treeChange)
    {
      new QWebChannel(socket, function(channel) {
        var backend = channel.objects.backend
        backend.handleTreePair(JSON.stringify(treeChange));
      });
    }
  
    const backendSelection = function(selectionChange)
    {
      new QWebChannel(socket, function(channel) {
        var backend = channel.objects.backend
        backend.handleSelection(JSON.stringify(selectionChange));
      });
    }

  const handleTreeParentChange = (event) => {
    var index = event.target.value
    var parent = treePair[index].name
    var checked = event.target.checked

    backendTreePair({name: "all", checked: checked, parent: parent})
    treePair[index].state.map((_, indexOfInteraction) => {
      treePair[index].state[indexOfInteraction] = checked
    })

    forceUpdate()
  };

  const handleTreeChildChange = (event) => {
    var name = event.target.name
    var checked = event.target.checked
    var index = event.target.value
    var parent = treePair[index].name
    backendTreePair({name: name, checked: checked, parent: parent});
    var indexOfInteraction = treePair[index].interactions.indexOf(name)
    treePair[index].state[indexOfInteraction] = checked

    forceUpdate()
  };

  const handleSelectionChange = (event) => {
    var index = event.target.value
    var checked = event.target.checked
    backendSelection({index: index, checked: checked})
    treeSelection[index].state = checked

    forceUpdate()
  } 

  const theme = {
    spacing: 8,
  }

  return (
    <div>
      <Popper open={interactionDisplayed} anchorEl={virtualElDisplayInteractionPopper}>
        <Widget>
          <Box component="section" sx={{
            width: 280,
            height: 170,
            display: "flex",
            flexDirection: "column",
            color: 'rgba(255, 255, 255, 0.8)',
            overflowY: "auto",
            "&::-webkit-scrollbar": {
              width: 8
            },
            "&::-webkit-scrollbar-track": {
              backgroundColor: 'rgba(255,255,255,0.2)'
            },
            "&::-webkit-scrollbar-thumb": {
              backgroundColor: 'rgba(33, 33, 33, 0.95)',
              borderRadius: 2
            }
          }}>
            {
              treePair.map((pair, index) => (
                <div key={pair.name}>
                  <FormControlLabel
                      label={
                        <Typography sx={{ fontSize: 16 }}>
                          {pair.name}
                        </Typography>
                        }
                      value={index}
                      control={
                        <Checkbox
                          sx={{ py: 0, '& .MuiSvgIcon-root': { fontSize: 16 } }}
                          checked={pair.state.every(element => element === true)}
                          indeterminate={
                            !(pair.state.every(element => element === true)) &&
                            !(pair.state.every(element => element === false))
                          }
                          onChange={handleTreeParentChange}
                        />
                      }
                    />
                    <Box id={pair.name} name={pair.name} sx={{ display: 'flex', flexDirection: 'column', ml: 2, my: 0 }}>
                    {
                      pair.interactions.map((interaction, int_index) => (
                        <FormControlLabel
                          key={interaction}
                          sx={{ my: 0 }}
                          name={interaction}
                          value={index}
                          label={
                            <Typography sx={{ fontSize: 16 }}>
                              {interaction}
                            </Typography>
                            }
                          control={
                            <Checkbox
                              sx={{ py: 0, '& .MuiSvgIcon-root': { fontSize: 16 } }}
                              checked={pair.state[int_index]}
                              onChange={handleTreeChildChange}
                            />}
                        />
                      ))
                    }
                    </Box>
                  </div>
              ))
            }
          </Box>
        </Widget>
        
      </Popper>
      <Popper open={true} anchorEl={virtualElDisplayInteractionButton}>
        <Avatar sx={{ bgcolor: 'rgba(152, 152, 152, 0.3)' }} style={{ border: '0.1px solid rgba(3, 200, 255, 0.5)' }}>
          <IconButton color="primary" onClick={() => {
            if (!interactionDisplayed) {setSelectionDisplayed(false)};
            setInteractionDisplayed(!interactionDisplayed);
          }}><Icon>visibility</Icon></IconButton>
        </Avatar>
      </Popper>

      <Popper open={selectionDisplayed} anchorEl={virtualElDisplaySelectionPopper}>
        <Widget>
          <Box component="section" sx={{
            // py: 1,
            width: 280,
            height: 170,
            display: "flex",
            flexDirection: "column",
            color: 'rgba(255, 255, 255, 0.8)',
            overflowY: "auto",
            "&::-webkit-scrollbar": {
              width: 8
            },
            "&::-webkit-scrollbar-track": {
              backgroundColor: 'rgba(255,255,255,0.2)'
            },
            "&::-webkit-scrollbar-thumb": {
              backgroundColor: 'rgba(33, 33, 33, 0.95)',
              borderRadius: 2
            }
          }}>
            {
              treeSelection.map((pair, index) => (
                <FormControlLabel
                  key={pair.name}
                  label={
                    <Typography sx={{ fontSize: 16 }}>
                      {pair.name}
                    </Typography>
                    }
                  value={index}
                  control={
                    <Checkbox
                      sx={{ py: 0, ml: 1, '& .MuiSvgIcon-root': { fontSize: 16 } }}
                      checked={pair.state}
                      onChange={handleSelectionChange}
                    />
                  }
                />
              ))
            }
          </Box>
        </Widget>
        
      </Popper>
      <Popper open={true} anchorEl={virtualElDisplaySelectionButton}>
        <Avatar sx={{ bgcolor: 'rgba(152, 152, 152, 0.3)' }} style={{ border: '0.1px solid rgba(3, 200, 255, 0.5)' }}>
          <IconButton color="primary" onClick={() => {
            if (!selectionDisplayed) {setInteractionDisplayed(false)};
            setSelectionDisplayed(!selectionDisplayed);
          }}><Icon>wysiwyg</Icon></IconButton>
        </Avatar>
        <Button id='treeforceUpdate' sx={{ display: 'none' }} onClick={forceUpdate}></Button>
      </Popper>
    </div>
  );
}