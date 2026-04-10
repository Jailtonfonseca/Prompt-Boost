import React from 'react';
import { diff_match_patch, DIFF_DELETE, DIFF_INSERT, DIFF_EQUAL } from 'diff-match-patch';
import './DiffDisplay.css';
import './LoadingSpinner.css';

const DiffDisplay = ({ text1, text2, isLoading }) => {
  if (isLoading) {
    return (
      <div className="loading-spinner">
        <div className="spinner"></div>
        <span>Otimizando seu prompt...</span>
      </div>
    );
  }

  if (!text2) {
    return (
      <div className="diff-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontFamily: 'inherit', fontSize: '0.95rem' }}>
        O resultado aparecerá aqui após a otimização
      </div>
    );
  }

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

  if (display.length === 0 || (display.length === 1 && display[0].props.children === '')) {
      return <div className="diff-container">{text1}</div>
  }

  return <div className="diff-container">{display}</div>;
};

export default DiffDisplay;
