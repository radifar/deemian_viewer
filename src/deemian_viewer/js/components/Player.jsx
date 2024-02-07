import * as React from 'react';
import { styled, useTheme } from '@mui/material/styles';
import Button from '@mui/material/Button'
import Box from '@mui/material/Box';
import Popper from '@mui/material/Popper';
import Typography from '@mui/material/Typography';
import Slider from '@mui/material/Slider';
import IconButton from '@mui/material/IconButton';
import PauseRounded from '@mui/icons-material/PauseRounded';
import PlayArrowRounded from '@mui/icons-material/PlayArrowRounded';
import SkipNext from '@mui/icons-material/SkipNext';
import SkipPrevious from '@mui/icons-material/SkipPrevious';
import TextField from '@mui/material/TextField';
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
    theme.palette.mode === 'dark' ? 'rgba(0,0,0,0.8)' : 'rgba(255,255,255,0.7)',
  // backdropFilter: 'blur(40px)',
}));

const TinyText = styled(Typography)({
  fontSize: '0.75rem',
  opacity: 0.38,
  fontWeight: 500,
  letterSpacing: 0.2,
});

export default function PlayerSlider({ virtualElPlayer, playerMinMax, socket }) {
  const theme = useTheme();
  const [enabled, setEnabled] = React.useState(false)
  const [position, setPosition] = React.useState(1);
  const [widgetWidth, setWidgetWidth] = React.useState(window.innerWidth - 240);
  const [paused, setPaused] = React.useState(true);
  const [textValue, setTextValue] = React.useState(1);

  React.useEffect(() => {
    const onResize = () => setWidgetWidth(Math.floor(window.innerWidth - 240))
    window.addEventListener('resize', onResize);
  }, []);

  const handleKeyPress = e => {
    if (e.keyCode === 13) {
      var newValue = parseInt(textValue)
      if (newValue < playerMinMax[1]) {
        setPosition(newValue);
      } else {
        setPosition(playerMinMax[1])
      }
      
    }
  };

  const handleNext = () => {
    if (position < playerMinMax[1]) {
      setPosition(position+1)
    } else {
      setPosition(playerMinMax[0])
    }
  }

  const handlePrevious = () => {
    if (position > playerMinMax[0]) {
      setPosition(position-1)
    } else {
      setPosition(playerMinMax[1])
    }
  }

  const mainIconColor = theme.palette.mode === 'dark' ? '#fff' : '#000';
  
  const enablePlayer = function () {
    setEnabled(true)
    setTextValue(playerMinMax[0])
    setPosition(playerMinMax[0])
  }

  const disablePlayer = function () {
    setEnabled(false)
  }

  React.useEffect(() => {
    const timer = setTimeout(() => {
      if (position < playerMinMax[1]) {
        !paused && setPosition(position+1)
      } else {
        !paused && setPosition(playerMinMax[0])
      }
      
    }, 850)
    return () => clearTimeout(timer)
   }, [position, paused])

   React.useEffect(() => {
    setTextValue(position)

    if (socket.readyState === WebSocket.OPEN) {
      new QWebChannel(socket, function(channel) {
        var x = {position: position}
        var backend = channel.objects.backend
        backend.setConformation(JSON.stringify(x));
      });
    }
   }, [position])
  
  return (
    <div>
      <Popper open={enabled} anchorEl={virtualElPlayer}>
        <Box sx={{ width: '100%', overflow: 'hidden' }}>
          <Widget width={widgetWidth}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                m: -1,
              }}
            >
              <IconButton
                aria-label={paused ? 'play' : 'pause'}
                onClick={() => setPaused(!paused)}
                sx = {{px:2}}
              >
                {paused ? (
                  <PlayArrowRounded
                    sx={{ fontSize: '1.5rem' }}
                    htmlColor={mainIconColor}
                  />
                ) : (
                  <PauseRounded sx={{ fontSize: '1.5rem' }} htmlColor={mainIconColor} />
                )}
              </IconButton>
              <Slider
                aria-label="time-indicator"
                size="small"
                value={position}
                min={playerMinMax[0]}
                step={1}
                max={playerMinMax[1]}
                onChange={(_, value) => {setPosition(value);}}
                sx={{
                  color: theme.palette.mode === 'dark' ? '#fff' : 'rgba(0,0,0,0.87)',
                  height: 4,
                  '& .MuiSlider-thumb': {
                    width: 8,
                    height: 8,
                    transition: '0.3s cubic-bezier(.47,1.64,.41,.8)',
                    '&::before': {
                      boxShadow: '0 2px 12px 0 rgba(0,0,0,0.4)',
                    },
                    '&:hover, &.Mui-focusVisible': {
                      boxShadow: `0px 0px 0px 8px ${
                        theme.palette.mode === 'dark'
                          ? 'rgb(255 255 255 / 16%)'
                          : 'rgb(0 0 0 / 16%)'
                      }`,
                    },
                    '&.Mui-active': {
                      width: 16,
                      height: 16,
                    },
                  },
                  '& .MuiSlider-rail': {
                    opacity: 0.28,
                  },
                }}
              />
              <IconButton onClick={handlePrevious} aria-label="previous frame">
                <SkipPrevious fontSize="medium" htmlColor={mainIconColor} />
              </IconButton>
              <TextField
                id="frame-number"
                value={textValue}
                onChange={e => setTextValue(e.target.value)}
                onKeyDown={handleKeyPress}
                size="small"
                inputProps={{
                  min: playerMinMax[0],
                  max: playerMinMax[1],
                  style: { textAlign: 'center' },
                }}
                sx={{ width: 120 }}
              />
              <IconButton onClick={handleNext} aria-label="next frame">
                <SkipNext fontSize="medium" htmlColor={mainIconColor} />
              </IconButton>
            </Box>
          </Widget>
        </Box>
      </Popper>
      <Button id='enablePlayer' sx={{ display: 'none' }} onClick={enablePlayer}></Button>
      <Button id='disablePlayer' sx={{ display: 'none' }} onClick={disablePlayer}></Button>
    </div>
    
  );
}