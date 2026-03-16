
import { type PropsWithChildren } from 'react';

const Dialog = ({ children }: PropsWithChildren) => {
  return (
    <div className="dialog-root dialog-visible">
      <div className="dialog-list">
        <div className="dialog-overlayer">
          <div className="dialog-item">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dialog;
