import { FormikConfig, FormikValues, useFormik } from 'formik';
import { useCallback } from 'react';

export const useForm = <Values extends FormikValues = FormikValues>(
  config: FormikConfig<Values>
) => {
  const { values, setFieldTouched, setFieldValue, handleChange, ...formik } =
    useFormik(config);

  const addField = useCallback(
    (field: string, newValue) => () => {
      setFieldValue(field, [...values[field], newValue], true);
    },
    [setFieldValue, values]
  );

  const removeField = useCallback(
    (field: string, index: number) => () => {
      setFieldValue(
        field,
        values[field].filter((_: unknown, i: number) => i !== index),
        true
      );
    },
    [setFieldValue, values]
  );

  return {
    ...formik,
    values,
    setFieldTouched,
    setFieldValue,
    handleChange: (
      e: React.ChangeEvent<HTMLTextAreaElement | HTMLInputElement>
    ) => {
      setFieldTouched(e.target.name);
      handleChange(e);
    },
    addField,
    removeField,
  };
};
