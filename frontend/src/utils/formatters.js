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
  const floorNumber = Number(floor);
  const floorsTotalNumber = Number(floorsTotal);
  if (!Number.isFinite(floorNumber) || floorNumber <= 0) return "";
  if (!Number.isFinite(floorsTotalNumber) || floorsTotalNumber <= 0) return `${floorNumber} этаж`;
  return `${floorNumber} из ${floorsTotalNumber}`;
};

export const safeNumber = (value) => {
  if (value === null || value === undefined) return null;
  const number = Number(value);
  return Number.isNaN(number) ? null : number;
};
