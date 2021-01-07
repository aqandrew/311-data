import React, { useState } from 'react';
import PropTypes from 'proptypes';
import { IconButton } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import SettingsSharpIcon from '@material-ui/icons/SettingsSharp';

const useStyles = makeStyles({
  gearIcon: {
    color: 'white',
    background: '#29404F',
    borderRadius: '12px',
    height: '33px',
    width: '33px',
    padding: '6px',
  },
  button: {
    padding: '0',
  },
});

const GearButton = props => {
  const { gearIcon, button } = useStyles();
  const [pressed, setPressed] = useState(false);
  const { onClick, style } = props;
  const onKeyDown = e => {
    e.preventDefault();
    if (e.key === ' '
        || e.key === 'Enter'
        || e.key === 'Spacebar'
    ) {
      setPressed(!pressed);
      onClick();
    }
  };
  const toggleClick = () => {
    setPressed(!pressed);
    onClick();
  };
  return (
    <IconButton
      className={button}
      onClick={toggleClick}
      onKeyDown={onKeyDown}
      role="button"
      aria-pressed={pressed}
      aria-label="Toggle Sidebar"
      style={style}
    >
      <SettingsSharpIcon className={gearIcon} />
    </IconButton>
  );
};

GearButton.propTypes = {
  onClick: PropTypes.func,
  style: PropTypes.obj,
};
GearButton.defaultProps = {
  onClick: undefined,
  style: undefined,
};

export default GearButton;
