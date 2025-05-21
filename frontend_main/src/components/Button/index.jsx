const Button = ({ onClick, text, buttonStyle }) => {
  return (
    <button
      className={`bg-brand-blue text-white py-1 px-7 rounded-lg cursor-pointer ${buttonStyle}`}
      onClick={onClick}
    >
      {text}
    </button>
  );
};

export default Button;
