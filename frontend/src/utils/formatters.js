export const formatPrice = (value) => {
  if (value === null || value === undefined) return "—";
  const number = Number(value);
  if (Number.isNaN(number)) return "—";
  return `${new Intl.NumberFormat("ru-RU").format(number)} ₽`;
};

export const formatArea = (value) => {
  if (value === null || value === undefined) return "—";
  const number = Number(value);
  if (Number.isNaN(number)) return "—";
  return `${number.toLocaleString("ru-RU")} м²`;
};

export const formatRooms = (rooms) => {
  if (rooms === null || rooms === undefined) return "Студия";
  return `${rooms}-комн.`;
};

export const formatFloor = (floor, floorsTotal) => {
  if (!floor || !floorsTotal) return "Этаж уточняется";
  return `${floor} из ${floorsTotal}`;
};

export const safeNumber = (value) => {
  if (value === null || value === undefined) return null;
  const number = Number(value);
  return Number.isNaN(number) ? null : number;
};
