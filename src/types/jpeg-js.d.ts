declare module 'jpeg-js' {
  export function decode(data: Uint8Array, options?: { useTArray?: boolean; formatAsRGBA?: boolean }): {
    width: number;
    height: number;
    data: Uint8Array;
  };
}
