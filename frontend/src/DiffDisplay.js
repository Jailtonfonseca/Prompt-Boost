import React from 'react';
import { diff_match_patch, DIFF_DELETE, DIFF_INSERT, DIFF_EQUAL } from 'diff-match-patch';
import './DiffDisplay.css';

const DiffDisplay = ({ text1, text2 }) => {
  const dmp = new diff_match_patch();
  const diffs = dmp.diff_main(text1, text2);
  dmp.diff_cleanupSemantic(diffs);

  const display = diffs.map(([op, data], index) => {
    switch (op) {
      case DIFF_INSERT:
        return <ins key={index}>{data}</ins>;
      case DIFF_DELETE:
        return <del key={index}>{data}</del>;
      case DIFF_EQUAL:
        return <span key={index}>{data}</span>;
      default:
        return null;
    }
  });

  return <div className="diff-container">{display}</div>;
};

export default DiffDisplay;
