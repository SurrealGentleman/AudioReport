import React, { useEffect, useState } from "react";
import { arrowDown } from "../../assets";

const Dropdown = ({
  title,
  color = "bg-brand-purple",
  objects,
  placeholder,
  onChangeSelect,
  displayProperty = "name",
  dropOpen,
  setDropOpen,
  clearable,
  validationError,
  selectedOptionValue,
  className,
  searchable,
  showArrow,
  readonly,
  hasBorder,
  renderTextField,
  searchFunction,
  multiple,
  initChecked,
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [, setSelectedOption] = useState(null);
  const [selectedIds, setSelectedIds] = useState([]);
  const [filteredOptions, setFilteredOptions] = useState(objects);

  useEffect(() => {
    if (selectedOptionValue && objects.length > 0) {
      let option;
      if (selectedOptionValue.id) {
        option = objects.find((obj) => obj.id === selectedOptionValue.id);
      } else {
        option = objects.find((obj) => obj.id === selectedOptionValue);
      }
      if (!option) {
        option = selectedOptionValue;
      }
      if (renderTextField) {
        const val = renderTextField(option);
        setSearchTerm(val);
      } else {
        setSearchTerm(option[displayProperty]);
      }
      setSelectedOption(option);
    }
  }, [displayProperty, objects, renderTextField, selectedOptionValue]);

  useEffect(() => {
    if (multiple && initChecked) {
      setSelectedIds(initChecked);
    }
  }, [initChecked]);

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleFocus = () => {
    setDropOpen(true);
  };

  const handleSelect = (option) => {
    if (!multiple) {
      setSelectedOption(option);
      if (renderTextField) {
        const val = renderTextField(option);
        setSearchTerm(val);
      } else {
        setSearchTerm(option[displayProperty]);
      }
      setDropOpen(false);
      onChangeSelect(option);
    } else {
      let newKeys = [];
      if (selectedIds.includes(option.id)) {
        newKeys = selectedIds.filter((el) => el !== option.id);
      } else {
        newKeys = [...selectedIds];
        newKeys.push(option.id);
      }
      setSelectedIds(newKeys);
      onChangeSelect(newKeys);
    }
  };

  useEffect(() => {
    const filterOptions = () => {
      if (searchTerm.trim() === "") {
        // Если поисковая строка пуста, показать все объекты
        setFilteredOptions(objects);
      } else {
        setFilteredOptions(
          objects.filter(
            searchFunction
              ? (option) => searchFunction(option, searchTerm)
              : (option) =>
                  option[displayProperty]
                    .toLowerCase()
                    .includes(searchTerm.toLowerCase())
          )
        );
      }
    };

    filterOptions();
  }, [searchTerm]);

  return (
    <div>
      {title && <p className=" text-xs text-gray-500">{title}</p>}
      <div className={`relative cursor-pointer z-15`}>
        <input
          type="text"
          maxLength={127}
          className={`overflow-ellipsis rounded-lg text-xs w-[130%] ${color} py-2 px-4 pr-10 ${
            validationError && "border border-red-600 p-1"
          }
            ${className} `}
          placeholder={placeholder}
          value={searchTerm}
          onChange={handleSearch}
          onFocus={handleFocus}
        />
        {validationError && (
          <p className={"text-red-500 text-xs ml-2"}>{validationError}</p>
        )}
        <div
          className={` ${dropOpen && !readonly ? "block" : "hidden"}
            absolute z-20 w-[130%] overflow-auto bg-white text-xs rounded-lg shadow-md max-h-72`}
        >
          {!multiple
            ? filteredOptions?.map((option) => (
                <div
                  key={option.id}
                  className="px-3 font-normal py-2 cursor-pointer hover:bg-gray-100"
                  style={{ color: option.color }}
                  onClick={() => handleSelect(option)}
                >
                  {option[displayProperty]}
                </div>
              ))
            : filteredOptions?.map((opt) => {
                return (
                  <div
                    key={opt.id}
                    className={
                      "px-3 font-normal py-2 cursor-pointer hover:bg-gray-100"
                    }
                    style={{ color: opt.color }}
                    onClick={() => handleSelect(opt)}
                  >
                    <input
                      type="checkbox"
                      checked={selectedIds.includes(opt.id)}
                      className="mr-1.5 cursor-pointer"
                      readOnly
                    />
                    {opt[displayProperty]}
                  </div>
                );
              })}
        </div>
        {searchTerm !== "" && clearable && !readonly && (
          <button
            className="text-sm"
            style={{
              position: "absolute",
              display: "inline-block",
              right: "-26px",
              top: "6px",
            }}
            onClick={() => {
              setSearchTerm("");
              setSelectedOption(null);
              onChangeSelect(null);
            }}
          >
            &#x2716;
          </button>
        )}
        {showArrow && !readonly && (
          <img
            className={`absolute -right-12 top-2 ${
              dropOpen && "transform rotate-180"
            }`}
            src={arrowDown}
            onClick={() => setDropOpen(!dropOpen)}
          />
        )}
      </div>
      {dropOpen && (
        <div
          className="fixed z-10 w-full h-full top-0 left-0"
          onClick={() => {
            setDropOpen(false);
          }}
        ></div>
      )}
    </div>
  );
};

export default Dropdown;
