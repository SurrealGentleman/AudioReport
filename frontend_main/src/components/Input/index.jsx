const Input = ({
  placeholder,
  type,
  title,
  onChange,
  onKeyPress,
  value,
  inputStyle,
  titleStyle,
  validationError,
}) => {
  return (
    <div>
      {title && (
        <div className="w-full flex mt-3 items-center text-lg">
          <p className={titleStyle}>{title}</p>
          <hr className="border-0.5 w-full ml-2" />
        </div>
      )}
      <input
        className={`bg-brand-grey rounded-lg px-3 py-1 w-full mt-1 ${
          validationError && "border border-red-600"
        } ${inputStyle}`}
        placeholder={placeholder}
        type={type}
        onChange={(e) => onChange(e)}
        value={value}
        onKeyPress={onKeyPress}
      />
    </div>
  );
};

export default Input;
