interface BirdProps {
  birdClassName?: string;
  birdBodyClassName?: string;
  headClassName?: string;
  leftWingClassName?: string;
  leftTopWingClassName?: string;
  rightWingClassName?: string;
  rightTopWingClassName?: string;
  leftTailClassName?: string;
  rightTailClassName?: string;
}


const OrigamiFlappyBird = ({
  birdClassName = "",
  birdBodyClassName = "",
  headClassName = "",
  leftWingClassName = "",
  leftTopWingClassName = "",
  rightWingClassName = "",
  rightTopWingClassName = "",
  leftTailClassName = "",
  rightTailClassName = ""
}: BirdProps) => {
  return (
    <div className={`bird ${birdClassName}`}>
      <div className={`bird-body ${birdBodyClassName}`}>
        <div className={`head ${headClassName}`}></div>
        <div className={`left-wing ${leftWingClassName}`}>
          <div className={`left-top-wing ${leftTopWingClassName}`}></div>
        </div>
        <div className={`right-wing ${rightWingClassName}`}>
          <div className={`right-top-wing ${rightTopWingClassName}`}></div>
        </div>
        <div className={`left-tail ${leftTailClassName}`}></div>
        <div className={`right-tail ${rightTailClassName}`}></div>
      </div>
    </div>
  );
};

export default OrigamiFlappyBird;
