import React, { useState, useCallback } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import moment from 'moment';
import SelectorBox from '@components/common/SelectorBox';
import DatePicker from '@components/common/DatePicker';
import {
  updateStartDate as reduxUpdateStartDate,
  updateEndDate as reduxUpdateEndDate,
} from '@reducers/filters';
import ArrowToolTip from '@components/common/ArrowToolTip';
import options from './options';
import useStyles from './useStyles';
import DateRanges from './DateRanges';

const dateFormat = 'YYYY-MM-DD';

function DateSelector({
  range,
  updateStartDate,
  updateEndDate,
}) {
  const [expanded, setExpanded] = useState(false);
  const classes = useStyles();

  const handleOptionSelect = optionDates => {
    const formattedStart = moment(optionDates[0]).format(dateFormat);
    const formattedEnd = moment(optionDates[1]).format(dateFormat);
    updateStartDate(formattedStart);
    updateEndDate(formattedEnd);
    setExpanded(false);
  };

  const closeOptionsOnDateToggle = useCallback(() => {
    setExpanded(false);
  }, []);

  const { option, selected, label, iconStyle, tooltipParagraph } = classes;

  const linkedinPageLink = <a href='https://www.linkedin.com/company/hack-for-la/'>LinkedIn Page</a>

  return (
    <>
      <span className={label}>
        Date Range&nbsp;
        <ArrowToolTip iconStyle={iconStyle}>
          <div>
            <p className={tooltipParagraph}>
              <strong>
                Currently, 311-Data loads only 311 service
                request data from 2023 onward.
              </strong>
            </p>
            <p className={tooltipParagraph}>
              For updates on the release of available 311
              Data, please follow our {linkedinPageLink}.
            </p>
          </div>
        </ArrowToolTip>
      </span>
      <SelectorBox onToggle={() => setExpanded(!expanded)} expanded={expanded}>
        <SelectorBox.Display>
          <div className={classes.selector}>
            <DatePicker
              range={range}
              onToggle={closeOptionsOnDateToggle}
            />
            <div className={classes.separator} />
          </div>
        </SelectorBox.Display>
        <SelectorBox.Collapse>
          <DateRanges
            classes={{ option, selected }}
            options={options}
            onSelect={handleOptionSelect}
          />
        </SelectorBox.Collapse>
      </SelectorBox>
    </>
  );
}

const mapDispatchToProps = dispatch => ({
  updateStartDate: date => dispatch(reduxUpdateStartDate(date)),
  updateEndDate: date => dispatch(reduxUpdateEndDate(date)),
});

export default connect(null, mapDispatchToProps)(DateSelector);

DateSelector.propTypes = {
  range: PropTypes.bool,
  updateStartDate: PropTypes.func.isRequired,
  updateEndDate: PropTypes.func.isRequired,
};

DateSelector.defaultProps = {
  range: false,
};
