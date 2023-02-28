export interface SelectMatrixOption {
  value: number;
  text: string;
  icon: React.ReactNode;
}

export interface SelectMatrixItemProps extends SelectMatrixOption {
  selected: boolean;
  onToggle: () => void;
}

export interface SelectMatrixProps {
  options?: SelectMatrixOption[];
  selected: number[];
  setSelected: React.Dispatch<React.SetStateAction<number[]>>;
  columns?: number;
}
